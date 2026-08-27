<template>
  <section class="accounts-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Finans · Cari</p>
        <h1>Cari Hesaplar</h1>
        <p>Müşteri borçlarını, ödemelerini ve hesap hareketlerini tek ekrandan takip edin.</p>
      </div>
      <button class="secondary" @click="refresh" :disabled="loading">↻ Yenile</button>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div class="summary-grid">
      <article class="summary-card"><span>Toplam müşteri</span><strong>{{ summary.customer_count }}</strong><small>cari kaydı</small></article>
      <article class="summary-card warning"><span>Toplam borç</span><strong>{{ money(summary.total_debt) }}</strong><small>{{ summary.customers_with_debt }} müşterinin borcu var</small></article>
      <article class="summary-card"><span>Toplam alacak</span><strong>{{ money(summary.total_credit) }}</strong><small>müşteri lehine bakiye</small></article>
      <article class="summary-card"><span>Net cari</span><strong>{{ money(summary.net_balance) }}</strong><small>borç − alacak</small></article>
    </div>

    <div class="accounts-layout">
      <section class="panel customer-panel">
        <div class="panel-head">
          <div><h2>Müşteri hesapları</h2><span>{{ customers.length }} kayıt</span></div>
          <input v-model="search" placeholder="Müşteri veya telefon ara..." @input="loadCustomers" />
        </div>
        <div v-if="loadingCustomers" class="empty">Hesaplar yükleniyor...</div>
        <div v-else-if="!customers.length" class="empty"><strong>Müşteri bulunamadı</strong><span>Tanımlar bölümünden müşteri ekleyebilirsiniz.</span></div>
        <div v-else class="customer-list">
          <button v-for="customer in customers" :key="customer.id" class="customer-row" :class="{ selected: selectedId === customer.id }" @click="selectCustomer(customer.id)">
            <div class="avatar">{{ initials(customer.name) }}</div>
            <div class="customer-main"><strong>{{ customer.name }}</strong><span>{{ customer.phone }} · {{ customer.vehicle_count }} araç</span></div>
            <div class="balance" :class="customer.balance_status"><small>{{ balanceLabel(customer) }}</small><strong>{{ money(Math.abs(customer.balance)) }}</strong></div>
          </button>
        </div>
      </section>

      <section class="panel detail-panel">
        <div v-if="!detail" class="empty detail-empty"><div class="detail-icon">₺</div><strong>Bir müşteri seçin</strong><span>Cari hareketlerini ve ödeme işlemlerini burada göreceksiniz.</span></div>
        <template v-else>
          <div class="detail-head">
            <div><p class="eyebrow">Müşteri hesabı</p><h2>{{ detail.customer.name }}</h2><span>{{ detail.customer.phone }}<template v-if="detail.customer.email"> · {{ detail.customer.email }}</template></span></div>
            <button class="primary" :disabled="detail.customer.balance <= 0" @click="openPayment">Ödeme Al</button>
          </div>

          <div class="balance-box" :class="detail.customer.balance_status">
            <span>Güncel bakiye</span>
            <strong>{{ money(Math.abs(detail.customer.balance)) }}</strong>
            <small>{{ balanceLabel(detail.customer) }}</small>
          </div>

          <div class="section-title"><h3>Hesap hareketleri</h3><span>Son 100 hareket</span></div>
          <div v-if="!detail.transactions.length" class="empty compact">Bu müşteriye ait cari hareket bulunmuyor.</div>
          <div v-else class="transaction-list">
            <div v-for="item in detail.transactions" :key="item.id" class="transaction-row">
              <div class="transaction-icon" :class="item.transaction_type">{{ item.transaction_type === 'debit' ? '↑' : '↓' }}</div>
              <div class="transaction-main"><strong>{{ transactionLabel(item) }}</strong><span>{{ item.description || '—' }}</span><small>{{ formatDate(item.created_at) }}</small></div>
              <strong class="transaction-amount" :class="item.transaction_type">{{ item.transaction_type === 'debit' ? '+' : '-' }}{{ money(item.amount) }}</strong>
            </div>
          </div>

          <div class="section-title sales-title"><h3>Son satışlar</h3><span>{{ detail.sales.length }} işlem</span></div>
          <div v-if="detail.sales.length" class="sales-mini">
            <div v-for="sale in detail.sales.slice(0, 6)" :key="sale.id"><strong>#{{ sale.id }}</strong><span>{{ formatDate(sale.created_at) }}</span><b>{{ money(sale.total_amount) }}</b></div>
          </div>
        </template>
      </section>
    </div>

    <section class="panel all-transactions">
      <div class="panel-head"><div><h2>Son cari hareketleri</h2><span>Tüm müşteriler</span></div></div>
      <div v-if="!transactions.length" class="empty compact">Henüz cari hareket bulunmuyor.</div>
      <div v-else class="table-wrap">
        <table><thead><tr><th>Tarih</th><th>Müşteri</th><th>İşlem</th><th>Açıklama</th><th class="right">Tutar</th></tr></thead>
          <tbody><tr v-for="item in transactions" :key="item.id"><td>{{ formatDate(item.created_at) }}</td><td>{{ customerName(item.customer_id) }}</td><td><span class="badge" :class="item.transaction_type">{{ transactionTypeLabel(item.transaction_type) }}</span></td><td>{{ item.description || '—' }}</td><td class="right"><strong :class="item.transaction_type">{{ item.transaction_type === 'debit' ? '+' : '-' }}{{ money(item.amount) }}</strong></td></tr></tbody>
        </table>
      </div>
    </section>

    <div v-if="paymentModal" class="backdrop" @click.self="paymentModal=false">
      <form class="modal" @submit.prevent="submitPayment">
        <div class="modal-head"><div><p class="eyebrow">Cari işlem</p><h2>Ödeme Al</h2></div><button type="button" class="close" @click="paymentModal=false">×</button></div>
        <div class="payment-info"><span>Mevcut borç</span><strong>{{ money(detail.customer.balance) }}</strong></div>
        <label>Ödeme tutarı *<input v-model.number="payment.amount" type="number" min="0.01" :max="detail.customer.balance" step="0.01" required /></label>
        <label>Ödeme yöntemi<select v-model="payment.payment_method"><option value="cash">Nakit</option><option value="card">Kart</option><option value="transfer">Havale/EFT</option><option value="other">Diğer</option></select></label>
        <label>Açıklama <span class="optional">(opsiyonel)</span><textarea v-model="payment.description" rows="3" placeholder="Ödeme hakkında not..." /></label>
        <div class="modal-actions"><button type="button" @click="paymentModal=false">Vazgeç</button><button class="primary" :disabled="saving">{{ saving ? 'Kaydediliyor...' : 'Ödemeyi Kaydet' }}</button></div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { getAccountCustomer, getAccountCustomers, getAccountSummary, getAccountTransactions, receivePayment } from "../services/accounts";

const summary = reactive({ customer_count: 0, customers_with_debt: 0, total_debt: 0, total_credit: 0, net_balance: 0 });
const customers = ref([]), transactions = ref([]), detail = ref(null), selectedId = ref(null);
const search = ref(""), loading = ref(false), loadingCustomers = ref(false), saving = ref(false), error = ref(""), success = ref(""), paymentModal = ref(false);
const payment = reactive({ amount: 0, payment_method: "cash", description: "" });
let searchTimer;
const money = value => `${Number(value || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`;
const formatDate = value => new Date(value).toLocaleString("tr-TR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
function initials(name) { return name.split(" ").slice(0, 2).map(x => x[0]).join("").toUpperCase(); }
function balanceLabel(c) { return c.balance > 0 ? "Borç" : c.balance < 0 ? "Alacak" : "Borç yok"; }
function transactionTypeLabel(type) { return type === "debit" ? "Borç" : type === "payment" ? "Ödeme" : "Alacak"; }
function transactionLabel(item) { return transactionTypeLabel(item.transaction_type); }
function customerName(id) { return customers.value.find(c => c.id === id)?.name || "Müşteri silinmiş"; }
async function loadCustomers() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(async () => {
    loadingCustomers.value = true;
    try { customers.value = await getAccountCustomers(search.value); }
    catch (e) { error.value = e.message; }
    finally { loadingCustomers.value = false; }
  }, 180);
}
async function selectCustomer(id) {
  selectedId.value = id; error.value = "";
  try { detail.value = await getAccountCustomer(id); }
  catch (e) { error.value = e.message; }
}
async function refresh() {
  loading.value = true; error.value = ""; success.value = "";
  try {
    const [s, c, t] = await Promise.all([getAccountSummary(), getAccountCustomers(search.value), getAccountTransactions()]);
    Object.assign(summary, s); customers.value = c; transactions.value = t;
    if (selectedId.value) detail.value = await getAccountCustomer(selectedId.value);
  } catch (e) { error.value = e.message; }
  finally { loading.value = false; }
}
function openPayment() { payment.amount = Number(detail.value.customer.balance); payment.payment_method = "cash"; payment.description = ""; paymentModal.value = true; }
async function submitPayment() {
  saving.value = true; error.value = ""; success.value = "";
  try {
    const result = await receivePayment(detail.value.customer.id, payment);
    paymentModal.value = false;
    success.value = `Ödeme kaydedildi. Yeni bakiye: ${money(result.new_balance)}.`;
    await refresh();
  } catch (e) { error.value = e.message; }
  finally { saving.value = false; }
}
onMounted(refresh);
</script>

<style scoped>
.accounts-page{padding:30px;max-width:1500px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.secondary{border:1px solid #dbe3ec;background:#fff;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px}.summary-card{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:18px}.summary-card span,.summary-card small{display:block;color:#64748b;font-size:12px}.summary-card strong{display:block;font-size:24px;margin:7px 0}.summary-card.warning strong{color:#b36a00}.accounts-layout{display:grid;grid-template-columns:440px minmax(0,1fr);gap:16px}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:15px;overflow:hidden}.panel-head{padding:16px 18px;border-bottom:1px solid #edf0f4;display:flex;justify-content:space-between;align-items:center;gap:15px}.panel-head h2{font-size:16px;margin:0}.panel-head span{font-size:12px;color:#64748b}.panel-head input{width:220px;border:1px solid #dbe3ec;border-radius:9px;padding:9px 11px}.customer-list{padding:7px}.customer-row{width:100%;display:flex;align-items:center;gap:11px;padding:12px 10px;border:0;border-bottom:1px solid #f0f2f5;background:#fff;text-align:left;cursor:pointer;border-radius:9px}.customer-row:hover,.customer-row.selected{background:#f1f8f7}.avatar{width:38px;height:38px;border-radius:10px;background:#e7f5f3;color:#0c7772;display:grid;place-items:center;font-weight:800;font-size:12px}.customer-main{min-width:0;flex:1}.customer-main strong,.customer-main span{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.customer-main strong{font-size:13px}.customer-main span{font-size:11px;color:#64748b;margin-top:3px}.balance{text-align:right}.balance small,.balance strong{display:block}.balance small{font-size:10px;color:#64748b}.balance strong{font-size:13px;margin-top:3px}.balance.debt strong,.transaction-amount.debit,td strong.debit{color:#b43d3d}.balance.credit strong,.transaction-amount.payment,td strong.payment{color:#19815e}.detail-panel{padding:20px}.detail-empty{height:100%;min-height:500px}.detail-icon{width:52px;height:52px;border-radius:14px;background:#e8f7f5;color:#0d746f;display:grid;place-items:center;font-size:25px;font-weight:800;margin-bottom:12px}.detail-head{display:flex;justify-content:space-between;align-items:flex-start;gap:15px}.detail-head h2{margin:4px 0;font-size:22px}.detail-head>div>span{font-size:12px;color:#64748b}.primary{border:0;border-radius:10px;padding:10px 15px;background:#128c8a;color:#fff;font-weight:750;cursor:pointer}.primary:disabled{opacity:.45;cursor:not-allowed}.balance-box{margin:18px 0;padding:18px;border-radius:12px;background:#f8fafc;border:1px solid #e6ebf0}.balance-box span,.balance-box small{display:block;color:#64748b;font-size:11px}.balance-box strong{display:block;font-size:28px;margin:5px 0}.balance-box.debt{background:#fff8f5;border-color:#f0dfd8}.balance-box.debt strong{color:#b43d3d}.balance-box.credit strong{color:#19815e}.section-title{display:flex;justify-content:space-between;align-items:center;margin:22px 0 10px}.section-title h3{font-size:14px;margin:0}.section-title span{font-size:11px;color:#94a3b8}.transaction-list{display:grid}.transaction-row{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #edf0f4}.transaction-icon{width:30px;height:30px;border-radius:8px;display:grid;place-items:center;font-weight:800}.transaction-icon.debit{background:#fdecec;color:#b43d3d}.transaction-icon.payment,.transaction-icon.credit{background:#eaf8f1;color:#19815e}.transaction-main{min-width:0;flex:1}.transaction-main strong,.transaction-main span,.transaction-main small{display:block}.transaction-main strong{font-size:12px}.transaction-main span{font-size:11px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.transaction-main small{font-size:10px;color:#94a3b8;margin-top:2px}.transaction-amount{font-size:12px}.sales-mini{display:grid;gap:5px}.sales-mini div{display:grid;grid-template-columns:60px 1fr auto;gap:10px;padding:8px 10px;background:#f8fafc;border-radius:8px;font-size:11px}.sales-mini span{color:#64748b}.all-transactions{margin-top:16px}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:760px}th,td{text-align:left;padding:13px 18px;border-bottom:1px solid #edf1f5;font-size:12px}th{font-size:10px;text-transform:uppercase;color:#7a8797;background:#fbfcfd}.right{text-align:right}.badge{display:inline-block;padding:4px 7px;border-radius:6px;font-size:10px;font-weight:800}.badge.debit{background:#fdecec;color:#a53b3b}.badge.payment{background:#eaf8f1;color:#187a59}.badge.credit{background:#eef0ff;color:#5660a8}.empty{text-align:center;padding:45px;color:#64748b}.empty strong,.empty span{display:block}.empty strong{color:#334155;margin-bottom:5px}.compact{padding:30px}.alert,.success{margin-bottom:14px;padding:12px 14px;border-radius:9px}.alert{background:#fbeaea;color:#a52e2e}.success{background:#eaf8f1;color:#187a59}.backdrop{position:fixed;inset:0;background:rgba(15,23,42,.48);display:grid;place-items:center;padding:20px;z-index:30}.modal{width:min(500px,100%);background:#fff;border-radius:16px;padding:22px;display:grid;gap:14px;box-shadow:0 25px 60px rgba(0,0,0,.2)}.modal-head{display:flex;justify-content:space-between;align-items:flex-start}.modal-head h2{margin:4px 0 0}.close{border:0;background:transparent;font-size:26px;cursor:pointer;color:#64748b}.modal label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155}.modal input,.modal select,.modal textarea{width:100%;border:1px solid #d8e0e8;border-radius:9px;padding:10px 11px;background:#fff}.optional{font-weight:500;color:#94a3b8}.payment-info{padding:13px;background:#f8fafc;border-radius:10px;display:flex;justify-content:space-between;align-items:center}.payment-info span{font-size:12px;color:#64748b}.payment-info strong{font-size:18px}.modal-actions{display:flex;justify-content:flex-end;gap:8px}.modal-actions button:not(.primary){border:1px solid #dbe3ec;background:#fff;border-radius:9px;padding:10px 14px;cursor:pointer}@media(max-width:1000px){.accounts-layout{grid-template-columns:1fr}.summary-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:650px){.accounts-page{padding:18px}.page-header{flex-direction:column;align-items:flex-start}.summary-grid{grid-template-columns:1fr 1fr}.panel-head{align-items:stretch;flex-direction:column}.panel-head input{width:100%}}
</style>
