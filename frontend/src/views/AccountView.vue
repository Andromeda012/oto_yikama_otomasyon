<template>
  <section class="accounts-page">
    <header class="page-header">
      <div><p class="eyebrow">Finans · Cari</p><h1>Cari Hesaplar</h1><p>Cari, araç, iş emri ve ödeme geçmişini tek müşteri görünümünde yönetin.</p></div>
      <button class="secondary" @click="refresh" :disabled="loading">↻ Yenile</button>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <section class="quick-panel panel">
      <div><p class="eyebrow">Hızlı Arama</p><h2>Plaka / Cari Bul</h2><span>Plaka, telefon veya müşteri adıyla arayın.</span></div>
      <div class="quick-search-wrap">
        <input v-model="quickQuery" placeholder="Örn. 34 ABC 123 veya 05XX..." @input="searchQuick" />
        <div v-if="quickResults.length" class="quick-results">
          <button v-for="item in quickResults" :key="`${item.vehicle_id}-${item.customer_id}`" @click="selectQuick(item)">
            <strong>{{ item.plate }}</strong><span>{{ item.customer }} · {{ item.vehicle }}</span><small>{{ item.phone }}</small>
          </button>
        </div>
      </div>
    </section>

    <div class="summary-grid">
      <article class="summary-card"><span>Toplam cari</span><strong>{{ summary.customer_count }}</strong><small>kayıt</small></article>
      <article class="summary-card warning"><span>Toplam borç</span><strong>{{ money(summary.total_debt) }}</strong><small>{{ summary.customers_with_debt }} müşterinin borcu var</small></article>
      <article class="summary-card"><span>Toplam alacak</span><strong>{{ money(summary.total_credit) }}</strong><small>müşteri lehine bakiye</small></article>
      <article class="summary-card"><span>Net cari</span><strong>{{ money(summary.net_balance) }}</strong><small>borç − alacak</small></article>
    </div>

    <div class="accounts-layout">
      <section class="panel customer-panel">
        <div class="panel-head"><div><h2>Cari hesaplar</h2><span>{{ customers.length }} kayıt</span></div><input v-model="search" placeholder="Cari veya telefon ara..." @input="loadCustomers" /></div>
        <div v-if="loadingCustomers" class="empty">Cari hesaplar yükleniyor...</div>
        <div v-else-if="!customers.length" class="empty"><strong>Cari bulunamadı</strong><span>Tanımlar bölümünden cari ekleyebilirsiniz.</span></div>
        <div v-else class="customer-list">
          <button v-for="customer in customers" :key="customer.id" class="customer-row" :class="{ selected: selectedId === customer.id }" @click="selectCustomer(customer.id)">
            <div class="avatar">{{ initials(customer.name) }}</div>
            <div class="customer-main"><strong>{{ customer.name }}</strong><span>{{ customer.phone }} · {{ customer.vehicle_count }} araç</span></div>
            <div class="balance" :class="customer.balance_status"><small>{{ balanceLabel(customer) }}</small><strong>{{ money(Math.abs(customer.balance)) }}</strong></div>
          </button>
        </div>
      </section>

      <section class="panel detail-panel">
        <div v-if="!detail" class="empty detail-empty"><div class="detail-icon">⌕</div><strong>Bir cari seçin</strong><span>Aracı, iş emirlerini, satışları ve cari hareketlerini birlikte göreceksiniz.</span></div>
        <template v-else>
          <div class="detail-head"><div><p class="eyebrow">Müşteri 360°</p><h2>{{ detail.customer.name }}</h2><span>{{ detail.customer.phone }}<template v-if="detail.customer.email"> · {{ detail.customer.email }}</template></span></div><button class="primary" :disabled="detail.customer.balance <= 0" @click="openPayment">Ödeme Al</button></div>

          <div class="balance-box" :class="detail.customer.balance_status"><span>Güncel bakiye</span><strong>{{ money(Math.abs(detail.customer.balance)) }}</strong><small>{{ balanceLabel(detail.customer) }}</small></div>

          <div class="section-title"><h3>Araçlar</h3><span>{{ detail.vehicles.length }} araç</span></div>
          <div v-if="!detail.vehicles.length" class="mini-empty">Bu cariye kayıtlı araç yok.</div>
          <div v-else class="vehicle-cards">
            <div v-for="vehicle in detail.vehicles" :key="vehicle.id" class="vehicle-card"><strong>{{ vehicle.plate }}</strong><span>{{ [vehicle.brand, vehicle.model].filter(Boolean).join(' ') || 'Araç' }}</span><small>{{ [vehicle.color, vehicle.year].filter(Boolean).join(' · ') || 'Detay yok' }}</small></div>
          </div>

          <div class="section-title"><h3>İşlem geçmişi</h3><span>{{ detail.jobs.length }} iş emri</span></div>
          <div v-if="!detail.jobs.length" class="mini-empty">Henüz iş emri bulunmuyor.</div>
          <div v-else class="job-list">
            <div v-for="job in detail.jobs.slice(0, 10)" :key="job.id" class="job-row"><div><strong>#{{ job.id }} · {{ job.plate }}</strong><span>{{ job.services.map(x => x.name).join(' · ') || 'Hizmet yok' }}</span><small>{{ formatDate(job.created_at) }}</small></div><div><strong>{{ money(job.total) }}</strong><span class="job-status">{{ jobStatus(job.status) }}</span></div></div>
          </div>

          <div class="section-title sales-title"><h3>Cari hareketleri</h3><span>{{ detail.transactions.length }} hareket</span></div>
          <div v-if="!detail.transactions.length" class="mini-empty">Cari hareketi bulunmuyor.</div>
          <div v-else class="transaction-list">
            <div v-for="item in detail.transactions.slice(0, 10)" :key="item.id" class="transaction-row"><div class="transaction-icon" :class="item.transaction_type">{{ item.transaction_type === 'debit' ? '↑' : '↓' }}</div><div class="transaction-main"><strong>{{ transactionTypeLabel(item.transaction_type) }}</strong><span>{{ item.description || '—' }}</span><small>{{ formatDate(item.created_at) }}</small></div><strong class="transaction-amount" :class="item.transaction_type">{{ item.transaction_type === 'debit' ? '+' : '-' }}{{ money(item.amount) }}</strong></div>
          </div>

          <div class="section-title"><h3>Son satışlar</h3><span>{{ detail.sales.length }} satış</span></div>
          <div v-if="!detail.sales.length" class="mini-empty">Bu cariye ait tamamlanmış satış bulunmuyor.</div>
          <div v-else class="sales-mini"><div v-for="sale in detail.sales.slice(0, 8)" :key="sale.id"><strong>#{{ sale.id }}</strong><span>{{ formatDate(sale.created_at) }}</span><b>{{ money(sale.total_amount) }}</b></div></div>
        </template>
      </section>
    </div>

    <section class="panel all-transactions">
      <div class="panel-head"><div><h2>Son cari hareketleri</h2><span>Tüm müşteriler</span></div></div>
      <div v-if="!transactions.length" class="empty compact">Henüz cari hareket bulunmuyor.</div>
      <div v-else class="table-wrap"><table><thead><tr><th>Tarih</th><th>Cari</th><th>İşlem</th><th>Açıklama</th><th class="right">Tutar</th></tr></thead><tbody><tr v-for="item in transactions" :key="item.id"><td>{{ formatDate(item.created_at) }}</td><td>{{ customerName(item.customer_id) }}</td><td><span class="badge" :class="item.transaction_type">{{ transactionTypeLabel(item.transaction_type) }}</span></td><td>{{ item.description || '—' }}</td><td class="right"><strong>{{ item.transaction_type === 'debit' ? '+' : '-' }}{{ money(item.amount) }}</strong></td></tr></tbody></table></div>
    </section>

    <div v-if="paymentModal" class="backdrop" @click.self="paymentModal=false"><form class="modal" @submit.prevent="submitPayment"><div class="modal-head"><div><p class="eyebrow">Cari işlem</p><h2>Ödeme Al</h2></div><button type="button" class="close" @click="paymentModal=false">×</button></div><div class="payment-info"><span>Mevcut borç</span><strong>{{ money(detail.customer.balance) }}</strong></div><label>Ödeme tutarı *<input v-model.number="payment.amount" type="number" min="0.01" :max="detail.customer.balance" step="0.01" required /></label><label>Ödeme yöntemi<select v-model="payment.payment_method"><option value="cash">Nakit</option><option value="card">Kart</option><option value="transfer">Havale/EFT</option><option value="other">Diğer</option></select></label><label>Açıklama <span class="optional">(opsiyonel)</span><textarea v-model="payment.description" rows="3" /></label><div class="modal-actions"><button type="button" @click="paymentModal=false">Vazgeç</button><button class="primary" :disabled="saving">{{ saving ? 'Kaydediliyor...' : 'Ödemeyi Kaydet' }}</button></div></form></div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { getAccountCustomer, getAccountCustomers, getAccountSummary, getAccountTransactions, quickSearchAccounts, receivePayment } from "../services/accounts";
const summary = reactive({ customer_count: 0, customers_with_debt: 0, total_debt: 0, total_credit: 0, net_balance: 0 });
const customers = ref([]), transactions = ref([]), detail = ref(null), selectedId = ref(null), quickResults = ref([]);
const search = ref(""), quickQuery = ref(""), loading = ref(false), loadingCustomers = ref(false), saving = ref(false), error = ref(""), success = ref(""), paymentModal = ref(false);
const payment = reactive({ amount: 0, payment_method: "cash", description: "" }); let searchTimer, quickTimer;
const money = value => `${Number(value || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`;
const formatDate = value => new Date(value).toLocaleString("tr-TR", { day:"2-digit", month:"2-digit", year:"numeric", hour:"2-digit", minute:"2-digit" });
function initials(name) { return name.split(" ").slice(0,2).map(x => x[0]).join("").toUpperCase(); }
function balanceLabel(c) { return c.balance > 0 ? "Borç" : c.balance < 0 ? "Alacak" : "Borç yok"; }
function transactionTypeLabel(type) { return type === "debit" ? "Borç" : type === "payment" ? "Ödeme" : "Alacak"; }
function customerName(id) { return customers.value.find(c => c.id === id)?.name || "Cari silinmiş"; }
function jobStatus(status) { return ({ waiting:"Bekliyor", checked_in:"İşleme alındı", washing:"Yıkamada", quality_check:"Kontrol", ready:"Hazır", delivered:"Teslim edildi", cancelled:"İptal" })[status] || status; }
async function loadCustomers() { clearTimeout(searchTimer); searchTimer = setTimeout(async () => { loadingCustomers.value=true; try { customers.value=await getAccountCustomers(search.value); } catch(e){error.value=e.message;} finally{loadingCustomers.value=false;} },180); }
async function selectCustomer(id) { selectedId.value=id; error.value=""; try{detail.value=await getAccountCustomer(id);}catch(e){error.value=e.message;} }
function selectQuick(item){ quickQuery.value=item.plate; quickResults.value=[]; selectCustomer(item.customer_id); }
function searchQuick(){ clearTimeout(quickTimer); if(quickQuery.value.trim().length<2){quickResults.value=[];return;} quickTimer=setTimeout(async()=>{try{quickResults.value=await quickSearchAccounts(quickQuery.value);}catch(e){error.value=e.message;}},180); }
async function refresh(){ loading.value=true; error.value=""; success.value=""; try{const [s,c,t]=await Promise.all([getAccountSummary(),getAccountCustomers(search.value),getAccountTransactions()]); Object.assign(summary,s); customers.value=c; transactions.value=t; if(selectedId.value) detail.value=await getAccountCustomer(selectedId.value);}catch(e){error.value=e.message;}finally{loading.value=false;} }
function openPayment(){payment.amount=Number(detail.value.customer.balance);payment.payment_method="cash";payment.description="";paymentModal.value=true;}
async function submitPayment(){saving.value=true;error.value="";try{const result=await receivePayment(detail.value.customer.id,payment);paymentModal.value=false;success.value=`Ödeme kaydedildi. Yeni bakiye: ${money(result.new_balance)}.`;await refresh();}catch(e){error.value=e.message;}finally{saving.value=false;}}
onMounted(refresh);
</script>

<style scoped>
.accounts-page{padding:30px;max-width:1500px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:18px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:10px;letter-spacing:.1em;font-weight:800}.primary,.secondary{border-radius:9px;padding:10px 14px;font-weight:750;cursor:pointer}.primary{border:0;background:#128c8a;color:#fff}.secondary{border:1px solid #cfd9e4;background:#fff;color:#334155}.primary:disabled,.secondary:disabled{opacity:.55;cursor:not-allowed}.alert,.success{padding:12px 14px;border-radius:9px;margin-bottom:14px}.alert{background:#fbeaea;color:#a52e2e}.success{background:#e8f7ef;color:#18734c}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:14px}.quick-panel{display:grid;grid-template-columns:1fr 1.3fr;gap:20px;padding:16px 18px;margin-bottom:14px}.quick-panel h2{margin:3px 0;font-size:16px}.quick-panel>div:first-child>span{font-size:11px;color:#64748b}.quick-search-wrap{position:relative}.quick-search-wrap>input{width:100%;border:1px solid #d8e0e8;border-radius:9px;padding:11px 12px}.quick-results{position:absolute;z-index:20;left:0;right:0;top:45px;background:#fff;border:1px solid #dbe3eb;border-radius:10px;box-shadow:0 12px 30px rgba(15,23,42,.12);overflow:hidden}.quick-results button{width:100%;display:grid;grid-template-columns:110px 1fr;gap:2px 10px;text-align:left;border:0;background:#fff;padding:11px 13px;cursor:pointer}.quick-results button:hover{background:#f7fafb}.quick-results strong{grid-row:1/3}.quick-results span,.quick-results small{font-size:11px;color:#64748b}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}.summary-card{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:16px 18px}.summary-card span,.summary-card small{display:block;color:#64748b;font-size:12px}.summary-card strong{display:block;font-size:25px;margin:5px 0}.summary-card.warning{border-color:#efd9a6}.accounts-layout{display:grid;grid-template-columns:minmax(320px,.85fr) minmax(0,1.45fr);gap:14px}.customer-panel{overflow:hidden}.panel-head{padding:15px 18px;border-bottom:1px solid #edf0f4;display:flex;justify-content:space-between;align-items:center;gap:12px}.panel-head h2{margin:0;font-size:16px}.panel-head span{display:block;font-size:11px;color:#64748b;margin-top:3px}.panel-head input{width:230px;border:1px solid #dbe3ec;border-radius:8px;padding:9px 10px}.customer-list{padding:6px}.customer-row{width:100%;display:grid;grid-template-columns:38px 1fr auto;gap:10px;align-items:center;border:0;background:#fff;border-radius:10px;padding:11px;cursor:pointer;text-align:left}.customer-row:hover,.customer-row.selected{background:#f2f9f8}.avatar{width:38px;height:38px;border-radius:10px;background:#e8f7f5;color:#0d746f;display:grid;place-items:center;font-size:12px;font-weight:800}.customer-main strong,.customer-main span{display:block}.customer-main strong{font-size:13px;color:#253244}.customer-main span{font-size:10px;color:#64748b;margin-top:3px}.balance{text-align:right}.balance small,.balance strong{display:block}.balance small{font-size:9px;color:#94a3b8}.balance strong{font-size:11px}.balance.debt strong{color:#b33434}.balance.credit strong{color:#287943}.detail-panel{padding:20px;min-height:520px}.detail-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start}.detail-head h2{margin:4px 0;font-size:21px}.detail-head span{font-size:11px;color:#64748b}.balance-box{margin:16px 0;padding:15px;border-radius:11px;background:#f7f9fb}.balance-box span,.balance-box small{display:block;color:#64748b;font-size:11px}.balance-box strong{display:block;font-size:25px;margin:4px 0}.balance-box.debt{background:#fff5f5}.balance-box.debt strong{color:#b33434}.section-title{display:flex;justify-content:space-between;align-items:center;margin:18px 0 9px}.section-title h3{margin:0;font-size:14px}.section-title span{font-size:10px;color:#94a3b8}.vehicle-cards{display:flex;gap:8px;flex-wrap:wrap}.vehicle-card{min-width:145px;border:1px solid #e5eaf0;border-radius:10px;padding:10px}.vehicle-card strong,.vehicle-card span,.vehicle-card small{display:block}.vehicle-card strong{font-size:12px}.vehicle-card span{font-size:11px;color:#475569;margin-top:4px}.vehicle-card small{font-size:9px;color:#94a3b8;margin-top:3px}.job-list{border-top:1px solid #edf1f5}.job-row{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid #edf1f5}.job-row>div:last-child{text-align:right}.job-row strong,.job-row span,.job-row small{display:block}.job-row strong{font-size:11px}.job-row span{font-size:10px;color:#64748b;margin-top:3px}.job-row small{font-size:9px;color:#94a3b8;margin-top:3px}.sales-mini{border-top:1px solid #edf1f5}.sales-mini>div{display:grid;grid-template-columns:60px 1fr auto;gap:8px;padding:9px 0;border-bottom:1px solid #edf1f5;font-size:10px}.sales-mini span{color:#64748b}.sales-mini b{text-align:right}.job-status{display:inline-block!important;margin-top:4px!important;padding:3px 6px;border-radius:5px;background:#eef6f5;color:#0d746f!important}.transaction-list{border-top:1px solid #edf1f5}.transaction-row{display:grid;grid-template-columns:30px 1fr auto;gap:9px;align-items:center;padding:9px 0;border-bottom:1px solid #edf1f5}.transaction-icon{width:28px;height:28px;border-radius:7px;display:grid;place-items:center;background:#eef2f6;color:#64748b;font-weight:800}.transaction-icon.debit{background:#fff0f0;color:#b33434}.transaction-icon.payment{background:#eaf7ee;color:#287943}.transaction-main strong,.transaction-main span,.transaction-main small{display:block}.transaction-main strong{font-size:11px}.transaction-main span{font-size:10px;color:#64748b;margin-top:2px}.transaction-main small{font-size:9px;color:#94a3b8;margin-top:2px}.transaction-amount{font-size:11px}.transaction-amount.debit{color:#b33434}.transaction-amount.payment{color:#287943}.all-transactions{margin-top:14px;overflow:hidden}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:700px}th,td{text-align:left;padding:12px 16px;border-bottom:1px solid #edf1f5;font-size:12px}th{font-size:10px;color:#7a8797;text-transform:uppercase}.right{text-align:right}.badge{display:inline-flex;padding:4px 7px;border-radius:999px;font-size:9px;font-weight:800}.badge.debit{background:#fff0f0;color:#b33434}.badge.payment{background:#eaf7ee;color:#287943}.badge.credit{background:#eef6ff;color:#3567a5}.empty{text-align:center;padding:45px 20px;color:#64748b}.empty strong,.empty span{display:block}.empty strong{color:#334155;margin-bottom:5px}.compact{padding:30px}.mini-empty{padding:10px 0;color:#94a3b8;font-size:11px}.detail-empty{min-height:450px;display:grid;place-items:center;align-content:center}.detail-icon{font-size:30px;color:#128c8a;margin-bottom:8px}.sales-title{margin-top:18px}.backdrop{position:fixed;inset:0;background:rgba(15,23,42,.48);display:grid;place-items:center;padding:20px;z-index:30}.modal{width:min(520px,100%);background:#fff;border-radius:15px;padding:22px;display:grid;gap:13px}.modal-head{display:flex;justify-content:space-between}.modal-head h2{margin:4px 0}.close{border:0;background:transparent;font-size:25px;cursor:pointer}.modal label{display:grid;gap:6px;font-size:12px;font-weight:700}.modal input,.modal select,.modal textarea{border:1px solid #d8e0e8;border-radius:8px;padding:10px}.payment-info{padding:12px;border-radius:9px;background:#f7f9fb;display:flex;justify-content:space-between}.modal-actions{display:flex;justify-content:flex-end;gap:8px}.modal-actions button:not(.primary){border:1px solid #dbe3ec;background:#fff;border-radius:8px;padding:9px 13px}.optional{font-weight:400;color:#94a3b8}@media(max-width:1050px){.summary-grid{grid-template-columns:1fr 1fr}.accounts-layout{grid-template-columns:1fr}.quick-panel{grid-template-columns:1fr}}@media(max-width:650px){.accounts-page{padding:18px}.page-header{align-items:flex-start;flex-direction:column}.summary-grid{grid-template-columns:1fr}.panel-head{align-items:stretch;flex-direction:column}.panel-head input{width:100%}.detail-panel{padding:16px}.detail-head{flex-direction:column}.detail-head .primary{width:100%}}
</style>
