<template>
  <section class="dashboard-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Genel Bakış</p>
        <h1>Dashboard</h1>
        <p>İşletmenizin bugünkü durumunu tek ekrandan takip edin.</p>
      </div>
      <div class="date-control">
        <button @click="changeDay(-1)" aria-label="Önceki gün">‹</button>
        <input v-model="selectedDate" type="date" @change="load" />
        <button @click="changeDay(1)" aria-label="Sonraki gün">›</button>
        <button class="today-button" @click="goToday">Bugün</button>
      </div>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div v-if="loading" class="loading">Dashboard verileri yükleniyor...</div>

    <template v-else>
      <div class="stat-grid">
        <article class="stat-card">
          <div class="stat-icon">◷</div>
          <div><span>Randevular</span><strong>{{ summary.appointment_count }}</strong><small>{{ summary.waiting_appointments }} bekleyen</small></div>
        </article>
        <article class="stat-card">
          <div class="stat-icon">🚗</div>
          <div><span>Aktif Araçlar</span><strong>{{ summary.active_jobs }}</strong><small>{{ summary.inspection_jobs }} kontrol aşamasında</small></div>
        </article>
        <article class="stat-card revenue">
          <div class="stat-icon">₺</div>
          <div><span>Günlük Ciro</span><strong>{{ money(summary.today_revenue) }}</strong><small>Hizmet {{ money(summary.service_revenue) }} · Market {{ money(summary.market_revenue) }}</small></div>
        </article>
        <article class="stat-card" :class="{ warning: summary.low_stock_count > 0 }">
          <div class="stat-icon">▥</div>
          <div><span>Kritik Stok</span><strong>{{ summary.low_stock_count }}</strong><small>{{ summary.low_stock_count ? 'Kontrol edilmesi gereken ürün' : 'Kritik stok bulunmuyor' }}</small></div>
        </article>
      </div>

      <div class="dashboard-grid">
        <section class="panel appointments-panel">
          <div class="panel-head"><div><p class="eyebrow">Günün Planı</p><h2>Randevular</h2></div><RouterLink to="/yonetim/randevu">Tümünü Gör →</RouterLink></div>
          <div v-if="!appointments.length" class="empty"><strong>Bugün için randevu yok.</strong><span>Randevu Yönetimi'nden yeni bir randevu oluşturabilirsiniz.</span><RouterLink class="primary-link" to="/yonetim/randevu">+ Yeni Randevu</RouterLink></div>
          <div v-else class="appointment-list">
            <RouterLink v-for="item in appointments" :key="item.id" class="appointment-row" to="/yonetim/randevu">
              <div class="time">{{ item.time }}</div>
              <div class="appointment-main"><strong>{{ item.plate }} · {{ item.vehicle }}</strong><span>{{ item.customer }} · {{ item.services.join(' · ') }}</span></div>
              <div class="appointment-right"><strong>{{ money(item.total_price) }}</strong><span :class="['status', item.status]">{{ statusLabel(item.status) }}</span></div>
            </RouterLink>
          </div>
        </section>

        <section class="panel actions-panel">
          <div class="panel-head"><div><p class="eyebrow">Kısayollar</p><h2>Hızlı İşlemler</h2></div></div>
          <div class="quick-actions">
            <RouterLink to="/yonetim/randevu"><b>＋</b><span><strong>Yeni Randevu</strong><small>Takvime yeni kayıt ekle</small></span></RouterLink>
            <RouterLink to="/yonetim/arac-takip"><b>🚗</b><span><strong>Araç Takibi</strong><small>Devam eden işleri yönet</small></span></RouterLink>
            <RouterLink to="/yonetim/market"><b>▣</b><span><strong>Satış Ekranı</strong><small>Market satışı oluştur</small></span></RouterLink>
            <RouterLink to="/tanimlar/hizmetler"><b>⚙</b><span><strong>Hizmet Tanımları</strong><small>Hizmet ve fiyatları yönet</small></span></RouterLink>
          </div>
          <div class="mini-info"><span>Toplam müşteri</span><strong>{{ summary.customer_count }}</strong></div>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { getDashboard } from "../services/dashboard";

const today = () => new Date().toLocaleDateString("en-CA");
const selectedDate = ref(today());
const loading = ref(true);
const error = ref("");
const summary = ref({ appointment_count: 0, waiting_appointments: 0, active_jobs: 0, inspection_jobs: 0, today_revenue: 0, market_revenue: 0, service_revenue: 0, low_stock_count: 0, customer_count: 0 });
const appointments = ref([]);

function money(value) { return `${Number(value || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`; }
function statusLabel(status) { return ({ scheduled: "Planlandı", arrived: "Geldi", in_service: "İşlemde", completed: "Tamamlandı", cancelled: "İptal" })[status] || status; }
async function load() { loading.value = true; error.value = ""; try { const data = await getDashboard(selectedDate.value); summary.value = data.summary; appointments.value = data.appointments; } catch (e) { error.value = e.message; } finally { loading.value = false; } }
function changeDay(offset) { const date = new Date(`${selectedDate.value}T12:00:00`); date.setDate(date.getDate() + offset); selectedDate.value = date.toLocaleDateString("en-CA"); load(); }
function goToday() { selectedDate.value = today(); load(); }
onMounted(load);
</script>

<style scoped>
.dashboard-page{padding:30px;max-width:1500px;margin:auto}.page-header{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin-bottom:24px}.page-header h1{margin:4px 0;font-size:30px;color:#172033}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#7b8797;text-transform:uppercase;font-size:10px;letter-spacing:.1em;font-weight:800}.date-control{display:flex;align-items:center;gap:6px}.date-control button,.date-control input{height:40px;border:1px solid #dce3ea;background:#fff;border-radius:9px;padding:0 12px;color:#334155}.date-control button{cursor:pointer;font-weight:700}.date-control input{font-size:13px}.date-control .today-button{color:#0f7774}.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.stat-card{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:18px;display:flex;gap:13px;align-items:flex-start}.stat-icon{width:40px;height:40px;border-radius:10px;background:#edf7f6;color:#128c8a;display:grid;place-items:center;font-weight:800}.stat-card span{display:block;font-size:11px;color:#64748b;font-weight:700}.stat-card strong{display:block;margin-top:5px;font-size:25px;color:#172033}.stat-card small{display:block;margin-top:4px;color:#94a3b8;font-size:10px}.stat-card.warning .stat-icon{background:#fff5df;color:#b7791f}.dashboard-grid{display:grid;grid-template-columns:1.55fr 1fr;gap:15px;margin-top:15px}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:20px}.panel-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:15px}.panel-head h2{margin:4px 0 0;font-size:17px}.panel-head a{font-size:12px;color:#128c8a;text-decoration:none;font-weight:700}.appointment-list{border-top:1px solid #edf0f4}.appointment-row{display:grid;grid-template-columns:65px 1fr auto;gap:15px;align-items:center;padding:14px 2px;border-bottom:1px solid #edf0f4;text-decoration:none;color:inherit}.appointment-row:last-child{border-bottom:0}.time{font-size:14px;font-weight:800;color:#172033}.appointment-main strong{display:block;font-size:13px}.appointment-main span{display:block;margin-top:4px;font-size:11px;color:#7b8797;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:520px}.appointment-right{text-align:right}.appointment-right strong{display:block;font-size:12px}.status{display:inline-block;margin-top:5px;padding:4px 7px;border-radius:6px;font-size:10px;font-weight:700;background:#eef2f6;color:#64748b}.status.arrived{background:#fff5df;color:#a66b00}.status.in_service{background:#e8f7f5;color:#0f7774}.status.completed{background:#eaf7ee;color:#287943}.empty{text-align:center;padding:38px 15px;color:#64748b}.empty strong,.empty span{display:block}.empty span{font-size:12px;margin-top:5px}.primary-link{display:inline-block;margin-top:16px;color:#128c8a;text-decoration:none;font-weight:750;font-size:12px}.quick-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}.quick-actions a{display:flex;align-items:center;gap:11px;border:1px solid #e5eaf0;border-radius:11px;padding:13px;text-decoration:none;color:#253044}.quick-actions a:hover{border-color:#a9d8d5;background:#f7fbfb}.quick-actions b{width:34px;height:34px;display:grid;place-items:center;border-radius:8px;background:#f1f5f8;color:#128c8a}.quick-actions strong,.quick-actions small{display:block}.quick-actions strong{font-size:12px}.quick-actions small{margin-top:3px;color:#8a95a3;font-size:10px}.mini-info{margin-top:16px;padding:14px;border-radius:10px;background:#f7f9fb;display:flex;justify-content:space-between;align-items:center}.mini-info span{font-size:11px;color:#64748b}.mini-info strong{font-size:18px}@media(max-width:1000px){.stat-grid{grid-template-columns:1fr 1fr}.dashboard-grid{grid-template-columns:1fr}}@media(max-width:650px){.dashboard-page{padding:18px}.page-header{align-items:flex-start;flex-direction:column}.date-control{width:100%}.date-control input{flex:1}.stat-grid{grid-template-columns:1fr}.appointment-row{grid-template-columns:50px 1fr}.appointment-right{display:none}.appointment-main span{max-width:calc(100vw - 150px)}.quick-actions{grid-template-columns:1fr}}
</style>
