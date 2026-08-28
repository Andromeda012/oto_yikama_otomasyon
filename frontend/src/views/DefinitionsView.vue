<template>
  <section class="definitions-page">
    <header class="page-header">
      <div><p class="eyebrow">Sistem Tanımları</p><h1>Tanımlar</h1><p>Cari, araç, hizmet, personel ve ürün bilgilerini tek yerden yönetin.</p></div>
      <button class="primary" @click="openCreate">+ Yeni {{ activeLabel }}</button>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.key" :class="{active: activeTab === tab.key}" @click="selectTab(tab.key)">{{ tab.label }} <span>{{ counts[tab.key] }}</span></button>
    </div>

    <section class="panel">
      <div class="panel-toolbar"><div><strong>{{ activeLabel }}</strong><span>{{ counts[activeTab] }} kayıt</span></div><input v-model="search" placeholder="Ara..." /></div>

      <div v-if="loading" class="empty">Kayıtlar yükleniyor...</div>
      <div v-else-if="filteredItems.length === 0" class="empty"><strong>Kayıt bulunamadı</strong><span>Yeni bir {{ activeLabel.toLowerCase() }} ekleyerek başlayabilirsiniz.</span></div>

      <div v-else class="table-wrap">
        <table>
          <thead><tr><th v-for="h in headers" :key="h.key">{{ h.label }}</th><th></th></tr></thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td v-for="h in headers" :key="h.key"><span :class="{muted: !item[h.key]}">{{ formatValue(item, h.key) }}</span></td>
              <td class="actions"><button @click="openEdit(item)">Düzenle</button><button class="danger" @click="remove(item)">{{ activeTab === 'services' || activeTab === 'staff' || activeTab === 'products' ? 'Pasifleştir' : 'Sil' }}</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="modal" class="backdrop" @click.self="modal=false">
      <form class="modal" @submit.prevent="save">
        <div class="modal-head"><div><p class="eyebrow">{{ editing ? 'Düzenle' : 'Yeni Kayıt' }}</p><h2>{{ activeLabel }}</h2></div><button type="button" class="close" @click="modal=false">×</button></div>

        <template v-if="activeTab === 'customers'">
          <div class="grid2"><label>Ad *<input v-model="form.first_name" required /></label><label>Soyad *<input v-model="form.last_name" required /></label></div>
          <label>Telefon *<input v-model="form.phone" required /></label><label>E-posta<input v-model="form.email" type="email" /></label><label>Not<textarea v-model="form.notes" rows="3" /></label>
        </template>
        <template v-else-if="activeTab === 'vehicles'">
          <label>Cari *<select v-model.number="form.customer_id" required><option value="" disabled>Seçin</option><option v-for="c in data.customers" :key="c.id" :value="c.id">{{ c.name }} — {{ c.phone }}</option></select></label>
          <div class="grid2"><label>Plaka *<input v-model="form.plate" required /></label><label>Renk<input v-model="form.color" /></label></div>
          <div class="grid2"><label>Marka<input v-model="form.brand" /></label><label>Model<input v-model="form.model" /></label></div><label>Model yılı<input v-model.number="form.year" type="number" min="1900" max="2100" /></label><label>Not<textarea v-model="form.notes" rows="3" /></label>
        </template>
        <template v-else-if="activeTab === 'services'">
          <label>Hizmet adı *<input v-model="form.name" required /></label>
          <div class="grid2"><label>Fiyat (TL) *<input v-model.number="form.price" type="number" min="0" step="0.01" required /></label><label>Süre (dk) *<input v-model.number="form.duration_minutes" type="number" min="1" required /></label></div>
          <label>Açıklama<textarea v-model="form.description" rows="3" /></label>
          <div class="materials-box">
            <div class="materials-head"><div><strong>Hizmette tüketilen stok</strong><span>İş emri teslim edildiğinde bu miktarlar stoktan düşer.</span></div></div>
            <div v-if="!data.products.length" class="mini-note">Önce Ürün / Stok bölümünden ürün tanımlayın.</div>
            <div v-else class="material-list">
              <div v-for="product in data.products.filter(x => x.is_active)" :key="product.id" class="material-row">
                <label class="material-check"><input type="checkbox" :checked="materialFor(product.id)" @change="toggleMaterial(product)" /><span>{{ product.name }} <small>{{ product.unit }}</small></span></label>
                <input v-if="materialFor(product.id)" v-model.number="materialFor(product.id).quantity" type="number" min="0.001" step="0.001" class="material-qty" />
              </div>
            </div>
          </div>
          <label class="check"><input v-model="form.is_active" type="checkbox" /> Aktif</label>
        </template>
        <template v-else-if="activeTab === 'staff'">
          <div class="grid2"><label>Ad *<input v-model="form.first_name" required /></label><label>Soyad *<input v-model="form.last_name" required /></label></div><label>Telefon<input v-model="form.phone" /></label><label>Görev / Rol<input v-model="form.role" placeholder="Örn. Yıkama Personeli" /></label><label class="check"><input v-model="form.is_active" type="checkbox" /> Aktif</label>
        </template>
        <template v-else>
          <label>Ürün adı *<input v-model="form.name" required /></label><div class="grid2"><label>SKU<input v-model="form.sku" /></label><label>Birim<input v-model="form.unit" placeholder="adet, litre..." /></label></div><div class="grid2"><label>Alış fiyatı<input v-model.number="form.purchase_price" type="number" min="0" step="0.01" /></label><label>Satış fiyatı<input v-model.number="form.sale_price" type="number" min="0" step="0.01" /></label></div><div class="grid2"><label>Mevcut stok<input v-model.number="form.stock_quantity" type="number" min="0" step="0.001" /></label><label>Minimum stok<input v-model.number="form.min_stock_level" type="number" min="0" step="0.001" /></label></div><label class="check"><input v-model="form.is_active" type="checkbox" /> Aktif</label>
        </template>

        <div class="modal-actions"><button type="button" @click="modal=false">Vazgeç</button><button class="primary" :disabled="saving">{{ saving ? 'Kaydediliyor...' : 'Kaydet' }}</button></div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createDefinition, deleteDefinition, getDefinitions, updateDefinition } from "../services/definitions";

const route = useRoute();
const router = useRouter();

const tabs = [
  { key: "customers", label: "Cari" },
  { key: "vehicles", label: "Araçlar" },
  { key: "services", label: "Hizmetler" },
  { key: "staff", label: "Personel" },
  { key: "products", label: "Ürün / Stok" },
];
const activeTab = ref("customers"), search = ref(""), loading = ref(false), saving = ref(false), modal = ref(false), editing = ref(null), error = ref("");
const routeToTab = { cari: "customers", araclar: "vehicles", hizmetler: "services", personel: "staff", urunler: "products" };
const tabToRoute = Object.fromEntries(Object.entries(routeToTab).map(([key, value]) => [value, key]));

function syncTabFromRoute() {
  const requested = routeToTab[route.params.subsection];
  if (requested) activeTab.value = requested;
}
function selectTab(tab) {
  activeTab.value = tab;
  router.replace({ name: "definitions", params: { subsection: tabToRoute[tab] } });
}
watch(() => route.params.subsection, syncTabFromRoute, { immediate: true });
const data = reactive({ customers: [], vehicles: [], services: [], staff: [], products: [] });
const blank = () => ({ first_name: "", last_name: "", phone: "", email: "", notes: "", customer_id: "", plate: "", brand: "", model: "", year: "", color: "", name: "", price: 0, duration_minutes: 30, description: "", is_active: true, role: "", sku: "", unit: "adet", purchase_price: 0, sale_price: 0, stock_quantity: 0, min_stock_level: 0, materials: [] });
const form = reactive(blank());
const activeLabel = computed(() => tabs.find(t => t.key === activeTab.value)?.label || "Kayıt");
const counts = computed(() => Object.fromEntries(tabs.map(t => [t.key, data[t.key].length])));
const headers = computed(() => ({
  customers: [{key:"name",label:"Cari"},{key:"phone",label:"Telefon"},{key:"email",label:"E-posta"},{key:"vehicle_count",label:"Araç"}],
  vehicles: [{key:"plate",label:"Plaka"},{key:"customer_name",label:"Cari"},{key:"brand",label:"Marka"},{key:"model",label:"Model"},{key:"color",label:"Renk"}],
  services: [{key:"name",label:"Hizmet"},{key:"price",label:"Fiyat"},{key:"duration_minutes",label:"Süre"},{key:"is_active",label:"Durum"}],
  staff: [{key:"name",label:"Personel"},{key:"phone",label:"Telefon"},{key:"role",label:"Görev"},{key:"is_active",label:"Durum"}],
  products: [{key:"name",label:"Ürün"},{key:"sku",label:"SKU"},{key:"stock_quantity",label:"Stok"},{key:"sale_price",label:"Satış"},{key:"is_active",label:"Durum"}],
})[activeTab.value]);
const filteredItems = computed(() => { const q = search.value.trim().toLocaleLowerCase("tr-TR"); if (!q) return data[activeTab.value]; return data[activeTab.value].filter(item => Object.values(item).some(v => String(v ?? "").toLocaleLowerCase("tr-TR").includes(q))); });
function materialFor(productId) { return form.materials.find(item => Number(item.product_id) === Number(productId)) || null; }
function toggleMaterial(product) { const existing = materialFor(product.id); if (existing) form.materials = form.materials.filter(item => Number(item.product_id) !== Number(product.id)); else form.materials.push({ product_id: product.id, quantity: product.unit === "adet" ? 1 : 0.001 }); }
function formatValue(item, key) { if (key === "is_active") return item[key] ? "Aktif" : "Pasif"; if (key === "price" || key === "sale_price" || key === "purchase_price") return `${Number(item[key] || 0).toLocaleString("tr-TR", {minimumFractionDigits: 2})} TL`; if (key === "duration_minutes") return `${item[key]} dk`; if (key === "stock_quantity") return `${item[key]} ${item.unit || ""}`; return item[key] || "—"; }
function openCreate() { editing.value = null; Object.assign(form, blank()); form.materials = []; modal.value = true; error.value = ""; }
function openEdit(item) { editing.value = item; Object.assign(form, blank(), item); form.materials = (item.materials || []).map(x => ({ product_id: x.product_id, quantity: x.quantity })); modal.value = true; error.value = ""; }
async function load() { loading.value = true; error.value = ""; try { Object.assign(data, await getDefinitions()); } catch (e) { error.value = e.message; } finally { loading.value = false; } }
async function save() { saving.value = true; error.value = ""; try { if (editing.value) await updateDefinition(activeTab.value, editing.value.id, form); else await createDefinition(activeTab.value, form); modal.value = false; await load(); } catch (e) { error.value = e.message; } finally { saving.value = false; } }
async function remove(item) { const message = activeTab.value === "services" || activeTab.value === "staff" || activeTab.value === "products" ? "Bu kaydı pasifleştirmek istediğinize emin misiniz?" : "Bu kaydı silmek istediğinize emin misiniz?"; if (!confirm(message)) return; try { await deleteDefinition(activeTab.value, item.id); await load(); } catch (e) { error.value = e.message; } }
onMounted(async () => {
  syncTabFromRoute();
  if (!route.params.subsection) router.replace({ name: "definitions", params: { subsection: "musteriler" } });
  await load();
});
</script>

<style scoped>
.definitions-page{padding:30px;max-width:1500px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.primary{border:0;border-radius:10px;padding:11px 16px;background:#128c8a;color:#fff;font-weight:750;cursor:pointer}.primary:disabled{opacity:.6;cursor:not-allowed}.tabs{display:flex;gap:6px;overflow:auto;margin-bottom:14px}.tabs button{white-space:nowrap;border:1px solid #e1e7ee;background:#fff;color:#526070;padding:10px 13px;border-radius:9px;font-weight:700;cursor:pointer}.tabs button span{margin-left:6px;color:#94a3b8}.tabs button.active{background:#e8f7f5;border-color:#a9ded9;color:#0d746f}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:15px;overflow:hidden}.panel-toolbar{padding:16px 18px;border-bottom:1px solid #edf0f4;display:flex;justify-content:space-between;align-items:center;gap:15px}.panel-toolbar strong{display:block}.panel-toolbar span{font-size:12px;color:#64748b}.panel-toolbar input{width:260px;border:1px solid #dbe3ec;border-radius:9px;padding:10px 12px}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:720px}th,td{text-align:left;padding:14px 18px;border-bottom:1px solid #edf1f5;font-size:13px}th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#7a8797;background:#fbfcfd}td{color:#334155}.muted{color:#94a3b8}.actions{white-space:nowrap;text-align:right}.actions button{border:1px solid #dbe3ec;background:#fff;border-radius:7px;padding:7px 9px;margin-left:6px;cursor:pointer}.actions .danger{color:#b33434}.empty{text-align:center;padding:55px;color:#64748b}.empty strong,.empty span{display:block}.empty strong{color:#334155;margin-bottom:5px}.alert{margin-bottom:14px;padding:12px 14px;border-radius:9px;background:#fbeaea;color:#a52e2e}.backdrop{position:fixed;inset:0;background:rgba(15,23,42,.48);display:grid;place-items:center;padding:20px;z-index:30}.modal{width:min(560px,100%);max-height:90vh;overflow:auto;background:#fff;border-radius:16px;padding:22px;display:grid;gap:14px;box-shadow:0 25px 60px rgba(0,0,0,.2)}.modal-head{display:flex;justify-content:space-between;align-items:flex-start}.modal-head h2{margin:4px 0 0}.close{border:0;background:transparent;font-size:26px;cursor:pointer;color:#64748b}.modal label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155}.modal input,.modal select,.modal textarea{width:100%;border:1px solid #d8e0e8;border-radius:9px;padding:10px 11px;background:#fff}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px} .materials-box{border:1px solid #e1e7ee;border-radius:10px;padding:12px;background:#fafcfd}.materials-head strong,.materials-head span{display:block}.materials-head strong{font-size:12px}.materials-head span{font-size:10px;color:#94a3b8;margin-top:3px}.material-list{margin-top:8px;border-top:1px solid #edf1f5}.material-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0;border-bottom:1px solid #edf1f5}.material-check{display:flex!important;align-items:center;gap:8px!important;font-weight:600!important}.material-check input{width:auto!important}.material-check span{font-size:11px}.material-check small{color:#94a3b8;font-weight:500}.material-qty{width:90px!important;padding:7px!important}.mini-note{font-size:10px;color:#94a3b8;margin-top:8px}.check{display:flex!important;grid-template-columns:none!important;align-items:center;gap:8px!important}.check input{width:auto}.modal-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:4px}.modal-actions button:not(.primary){border:1px solid #dbe3ec;background:#fff;border-radius:9px;padding:10px 14px;cursor:pointer}@media(max-width:720px){.definitions-page{padding:18px}.page-header{align-items:flex-start;flex-direction:column}.panel-toolbar{align-items:stretch;flex-direction:column}.panel-toolbar input{width:100%}.grid2{grid-template-columns:1fr}}
</style>
