<template>
  <section class="market-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Yönetim · Market</p>
        <h1>Market Satış</h1>
        <p>Ürün satışını, stoğu ve ödemeyi tek ekrandan yönetin.</p>
      </div>
      <button class="secondary" @click="refreshAll" :disabled="loading">↻ Yenile</button>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div class="summary-grid">
      <article class="summary-card"><span>Bugünkü satış</span><strong>{{ summary.today_sales }}</strong><small>tamamlanan işlem</small></article>
      <article class="summary-card"><span>Bugünkü ciro</span><strong>{{ money(summary.today_total) }}</strong><small>market satışları</small></article>
      <article class="summary-card"><span>Aktif ürün</span><strong>{{ summary.product_count }}</strong><small>satışa açık ürün</small></article>
      <article class="summary-card" :class="{ warning: summary.low_stock_count > 0 }"><span>Düşük stok</span><strong>{{ summary.low_stock_count }}</strong><small>minimum seviyede veya altında</small></article>
    </div>

    <div class="market-layout">
      <section class="panel products-panel">
        <div class="panel-head">
          <div><h2>Ürünler</h2><span>{{ filteredProducts.length }} ürün</span></div>
          <input v-model="search" @input="debouncedSearch" placeholder="Ürün veya SKU ara..." />
        </div>

        <div v-if="productsLoading" class="empty">Ürünler yükleniyor...</div>
        <div v-else-if="filteredProducts.length === 0" class="empty"><strong>Ürün bulunamadı</strong><span>Tanımlar bölümünden aktif ürün ekleyebilirsiniz.</span></div>
        <div v-else class="product-grid">
          <button v-for="product in filteredProducts" :key="product.id" class="product-card" :disabled="product.out_of_stock" @click="addToCart(product)">
            <div class="product-top"><span class="sku">{{ product.sku || 'SKU yok' }}</span><span v-if="product.low_stock" class="stock-warning">{{ product.out_of_stock ? 'Stok yok' : 'Düşük stok' }}</span></div>
            <strong>{{ product.name }}</strong>
            <div class="product-bottom"><span>{{ money(product.sale_price) }} / {{ product.unit }}</span><small>{{ number(product.stock_quantity) }} {{ product.unit }}</small></div>
          </button>
        </div>
      </section>

      <aside class="panel cart-panel">
        <div class="panel-head"><div><h2>Sepet</h2><span>{{ cartCount }} kalem</span></div><button v-if="cart.length" class="text-button danger" @click="clearCart">Temizle</button></div>

        <div v-if="!cart.length" class="cart-empty"><div class="cart-icon">🛒</div><strong>Sepet boş</strong><span>Satışa eklemek için soldan bir ürün seçin.</span></div>
        <div v-else class="cart-list">
          <div v-for="item in cart" :key="item.product_id" class="cart-row">
            <div class="cart-info"><strong>{{ item.name }}</strong><small>{{ money(item.unit_price) }} / {{ item.unit }}</small></div>
            <div class="quantity"><button @click="changeQuantity(item, -1)">−</button><input v-model.number="item.quantity" @change="normalizeQuantity(item)" type="number" min="1" :max="item.max_stock" step="0.001" /><button @click="changeQuantity(item, 1)">+</button></div>
            <strong class="line-total">{{ money(item.unit_price * item.quantity) }}</strong>
          </div>
        </div>

        <div class="sale-form" :class="{ disabled: !cart.length }">
          <label>Müşteri <span class="optional">(opsiyonel)</span><select v-model="form.customer_id"><option value="">Peşin / müşteri seçilmedi</option><option v-for="customer in lookups.customers" :key="customer.id" :value="customer.id">{{ customer.name }} — {{ customer.phone }}</option></select></label>
          <label>Satışı yapan personel<select v-model="form.staff_id"><option value="">Seçin</option><option v-for="staff in lookups.staff" :key="staff.id" :value="staff.id">{{ staff.name }}<span v-if="staff.role"> — {{ staff.role }}</span></option></select></label>
          <div class="payment-tabs"><button :class="{ active: form.payment_status === 'paid' }" @click="form.payment_status = 'paid'">Ödendi</button><button :class="{ active: form.payment_status === 'unpaid' }" @click="form.payment_status = 'unpaid'">Veresiye</button></div>
          <label v-if="form.payment_status === 'paid'">Ödeme yöntemi<select v-model="form.payment_method"><option v-for="method in lookups.payment_methods" :key="method.value" :value="method.value">{{ method.label }}</option></select></label>
          <div class="total-row"><span>Toplam</span><strong>{{ money(cartTotal) }}</strong></div>
          <button class="primary checkout" :disabled="!cart.length || saving" @click="completeSale">{{ saving ? 'Satış kaydediliyor...' : 'Satışı Tamamla' }}</button>
        </div>
      </aside>
    </div>

    <section class="panel recent-panel">
      <div class="panel-head"><div><h2>Son satışlar</h2><span>En son tamamlanan market işlemleri</span></div></div>
      <div v-if="sales.length === 0" class="empty compact">Henüz market satışı bulunmuyor.</div>
      <div v-else class="sales-table-wrap">
        <table><thead><tr><th>Satış</th><th>Tarih</th><th>Müşteri</th><th>Kalem</th><th>Ödeme</th><th class="right">Tutar</th></tr></thead>
          <tbody><tr v-for="sale in sales" :key="sale.id"><td><strong>#{{ sale.id }}</strong></td><td>{{ formatDate(sale.created_at) }}</td><td>{{ sale.customer?.name || 'Peşin satış' }}</td><td>{{ sale.items.length }} ürün</td><td><span class="badge" :class="sale.payment_status">{{ sale.payment_status === 'paid' ? `Ödendi · ${sale.payment_method_label}` : 'Veresiye' }}</span></td><td class="right"><strong>{{ money(sale.total_amount) }}</strong></td></tr></tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { createMarketSale, getMarketLookups, getMarketProducts, getMarketSummary, getRecentSales } from "../services/market";

const products = ref([]), sales = ref([]), search = ref(""), loading = ref(false), productsLoading = ref(false), saving = ref(false), error = ref(""), success = ref("");
const summary = reactive({ product_count: 0, low_stock_count: 0, today_sales: 0, today_total: 0 });
const lookups = reactive({ customers: [], staff: [], payment_methods: [] });
const cart = ref([]);
const form = reactive({ customer_id: "", staff_id: "", payment_status: "paid", payment_method: "cash" });
let searchTimer;
const filteredProducts = computed(() => products.value);
const cartCount = computed(() => cart.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0));
const cartTotal = computed(() => cart.value.reduce((sum, item) => sum + Number(item.unit_price || 0) * Number(item.quantity || 0), 0));
const money = value => `${Number(value || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`;
const number = value => Number(value || 0).toLocaleString("tr-TR", { maximumFractionDigits: 3 });

async function loadProducts() { productsLoading.value = true; try { products.value = await getMarketProducts(search.value); } catch (e) { error.value = e.message; } finally { productsLoading.value = false; } }
async function loadSummary() { Object.assign(summary, await getMarketSummary()); }
async function loadSales() { sales.value = await getRecentSales(); }
async function loadLookups() { Object.assign(lookups, await getMarketLookups()); }
async function refreshAll() { loading.value = true; error.value = ""; try { await Promise.all([loadProducts(), loadSummary(), loadSales(), loadLookups()]); } catch (e) { error.value = e.message; } finally { loading.value = false; } }
function debouncedSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(loadProducts, 250); }
function addToCart(product) { const existing = cart.value.find(item => item.product_id === product.id); if (existing) { if (existing.quantity < existing.max_stock) existing.quantity += 1; else error.value = `${product.name} için stok sınırına ulaştınız.`; return; } cart.value.push({ product_id: product.id, name: product.name, unit: product.unit, unit_price: Number(product.sale_price), quantity: 1, max_stock: Number(product.stock_quantity) }); error.value = ""; }
function changeQuantity(item, delta) {
  const step = item.unit === "adet" ? 1 : 0.001;
  const next = Math.round((Number(item.quantity) + delta * step) * 1000) / 1000;
  if (next <= 0) cart.value = cart.value.filter(x => x !== item);
  else if (next <= item.max_stock) item.quantity = next;
}
function normalizeQuantity(item) {
  let q = Number(item.quantity);
  if (!Number.isFinite(q) || q <= 0) q = item.unit === "adet" ? 1 : 0.001;
  q = Math.round(Math.max(0.001, Math.min(q, item.max_stock)) * 1000) / 1000;
  if (item.unit === "adet") q = Math.max(1, Math.round(q));
  item.quantity = q;
}
function clearCart() { cart.value = []; }
function formatDate(value) { return new Date(value).toLocaleString("tr-TR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }); }
async function completeSale() {
  error.value = ""; success.value = "";
  if (!cart.value.length) return;
  if (form.payment_status === "unpaid" && !form.customer_id) { error.value = "Veresiye satış için müşteri seçmelisiniz."; return; }
  if (!confirm(`${money(cartTotal.value)} tutarında satışı tamamlamak istiyor musunuz?`)) return;
  saving.value = true;
  try {
    const sale = await createMarketSale({ customer_id: form.customer_id || null, staff_id: form.staff_id || null, payment_status: form.payment_status, payment_method: form.payment_status === "paid" ? form.payment_method : null, items: cart.value.map(item => ({ product_id: item.product_id, quantity: item.quantity })) });
    success.value = `Satış #${sale.id} başarıyla tamamlandı. Toplam ${money(sale.total_amount)}.`;
    cart.value = [];
    form.customer_id = ""; form.payment_status = "paid"; form.payment_method = "cash";
    await Promise.all([loadProducts(), loadSummary(), loadSales()]);
  } catch (e) { error.value = e.message; } finally { saving.value = false; }
}
onMounted(async () => { try { await Promise.all([loadProducts(), loadSummary(), loadSales(), loadLookups()]); } catch (e) { error.value = e.message; } });
</script>

<style scoped>
.market-page{padding:30px;max-width:1550px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.primary,.secondary{border-radius:10px;padding:11px 16px;font-weight:750;cursor:pointer}.primary{border:0;background:#128c8a;color:#fff}.secondary{border:1px solid #cfd9e4;background:#fff;color:#334155}.primary:disabled,.secondary:disabled{opacity:.55;cursor:not-allowed}.alert,.success{padding:12px 14px;border-radius:9px;margin-bottom:14px}.alert{background:#fbeaea;color:#a52e2e}.success{background:#e8f7ef;color:#18734c}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}.summary-card{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:16px 18px}.summary-card span,.summary-card small{display:block;color:#64748b;font-size:12px}.summary-card strong{display:block;font-size:25px;margin:5px 0}.summary-card.warning{border-color:#efd9a6}.market-layout{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(360px,.9fr);gap:14px;align-items:start}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:15px;overflow:hidden}.panel-head{padding:16px 18px;border-bottom:1px solid #edf0f4;display:flex;justify-content:space-between;align-items:center;gap:15px}.panel-head h2{margin:0;font-size:16px}.panel-head span{font-size:12px;color:#64748b}.panel-head input{width:260px;border:1px solid #dbe3ec;border-radius:9px;padding:10px 12px}.product-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:14px}.product-card{text-align:left;border:1px solid #e2e8f0;background:#fff;border-radius:12px;padding:14px;cursor:pointer;min-height:130px;display:flex;flex-direction:column}.product-card:hover:not(:disabled){border-color:#9ed9d5;box-shadow:0 4px 15px rgba(15,118,110,.08)}.product-card:disabled{opacity:.55;cursor:not-allowed}.product-top{display:flex;justify-content:space-between;gap:8px;margin-bottom:12px}.sku{font-size:10px;color:#94a3b8}.stock-warning{font-size:10px;color:#a46b00;font-weight:800}.product-card>strong{font-size:14px;color:#253244;line-height:1.35}.product-bottom{margin-top:auto;padding-top:12px;display:flex;justify-content:space-between;gap:8px;align-items:end}.product-bottom span{font-weight:800;color:#0d746f;font-size:13px}.product-bottom small{color:#64748b;font-size:11px}.cart-panel{position:sticky;top:15px}.text-button{border:0;background:transparent;color:#64748b;font-size:12px;font-weight:750;cursor:pointer}.text-button.danger{color:#b33434}.cart-list{padding:6px 18px;max-height:360px;overflow:auto}.cart-row{display:grid;grid-template-columns:1fr auto auto;align-items:center;gap:10px;padding:12px 0;border-bottom:1px solid #edf1f5}.cart-info strong,.cart-info small{display:block}.cart-info strong{font-size:13px}.cart-info small{font-size:11px;color:#64748b;margin-top:3px}.quantity{display:flex;align-items:center;border:1px solid #dbe3ec;border-radius:8px;overflow:hidden}.quantity button{border:0;background:#f8fafc;width:28px;height:30px;cursor:pointer}.quantity input{border:0;border-left:1px solid #edf1f5;border-right:1px solid #edf1f5;width:38px;text-align:center;height:30px}.line-total{font-size:12px;min-width:70px;text-align:right}.sale-form{border-top:1px solid #edf1f5;padding:16px 18px;display:grid;gap:12px}.sale-form.disabled{opacity:.6}.sale-form label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155}.sale-form select{border:1px solid #d8e0e8;border-radius:9px;padding:10px;background:#fff}.optional{font-weight:500;color:#94a3b8}.payment-tabs{display:grid;grid-template-columns:1fr 1fr;background:#f3f6f8;border-radius:9px;padding:3px;gap:3px}.payment-tabs button{border:0;background:transparent;border-radius:7px;padding:9px;cursor:pointer;font-weight:750;color:#64748b}.payment-tabs button.active{background:#fff;color:#0d746f;box-shadow:0 1px 4px rgba(15,23,42,.08)}.total-row{display:flex;justify-content:space-between;align-items:center;padding-top:4px}.total-row span{color:#64748b}.total-row strong{font-size:24px;color:#0d746f}.checkout{width:100%;margin-top:2px}.cart-empty{padding:45px 20px;text-align:center;color:#64748b}.cart-icon{font-size:32px;margin-bottom:10px}.cart-empty strong,.cart-empty span{display:block}.cart-empty strong{color:#334155;margin-bottom:5px}.empty{text-align:center;padding:45px;color:#64748b}.empty strong,.empty span{display:block}.empty strong{color:#334155;margin-bottom:5px}.recent-panel{margin-top:14px}.sales-table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:760px}th,td{text-align:left;padding:13px 18px;border-bottom:1px solid #edf1f5;font-size:12px}th{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:#7a8797;background:#fbfcfd}.right{text-align:right}.badge{display:inline-flex;border-radius:999px;padding:5px 8px;font-size:10px;font-weight:800}.badge.paid{background:#e8f7ef;color:#18734c}.badge.unpaid{background:#fff4de;color:#a46b00}.compact{padding:30px}@media(max-width:1100px){.product-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.market-layout{grid-template-columns:1fr}.cart-panel{position:static}.summary-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:680px){.market-page{padding:18px}.page-header{align-items:flex-start;flex-direction:column}.page-header .secondary{width:100%}.summary-grid,.product-grid{grid-template-columns:1fr}.panel-head{align-items:stretch;flex-direction:column}.panel-head input{width:100%}.cart-row{grid-template-columns:1fr auto}.line-total{grid-column:2}.quantity{grid-column:2;grid-row:1}.line-total{grid-row:2}}
</style>
