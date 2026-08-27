<template>
  <section class="stats-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Raporlama</p>
        <h1>İstatistikler</h1>
        <p>Satış, hizmet, market ve operasyon performansını tek ekrandan inceleyin.</p>
      </div>
      <div class="period-actions">
        <button v-for="item in periods" :key="item.key" :class="['period-btn', {active: period === item.key}]" @click="setPeriod(item.key)">{{ item.label }}</button>
      </div>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div v-if="loading" class="loading">İstatistikler yükleniyor...</div>

    <template v-else>
      <div class="summary-grid">
        <article class="metric"><span>Toplam Ciro</span><strong>{{ money(summary.revenue) }}</strong><small :class="changeClass(summary.revenue_change)">{{ changeText(summary.revenue_change) }} önceki döneme göre</small></article>
        <article class="metric"><span>Hizmet Cirosu</span><strong>{{ money(summary.service_revenue) }}</strong><small>{{ summary.delivered_jobs }} araç teslim edildi</small></article>
        <article class="metric"><span>Market Cirosu</span><strong>{{ money(summary.market_revenue) }}</strong><small>{{ summary.sale_count }} satış · Ort. {{ money(summary.average_sale) }}</small></article>
        <article class="metric"><span>Cari Hareket</span><strong>{{ money(summary.period_payments) }}</strong><small>{{ money(summary.period_debit) }} dönem borcu işlendi</small></article>
      </div>

      <div class="grid two">
        <section class="panel chart-panel">
          <div class="panel-title"><div><h2>Günlük Ciro</h2><span>{{ dateRange }}</span></div></div>
          <div v-if="dailyMax === 0" class="empty">Bu dönemde henüz satış verisi yok.</div>
          <div v-else class="bar-chart">
            <div v-for="day in visibleDaily" :key="day.date" class="bar-item" :title="`${day.label}: ${money(day.revenue)}`">
              <div class="bar-track"><div class="bar" :style="{height: `${Math.max(3, (day.revenue / dailyMax) * 100)}%`}"></div></div>
              <span>{{ day.label }}</span>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-title"><div><h2>Randevu Performansı</h2><span>Seçilen dönem</span></div></div>
          <div class="appointment-stats">
            <div><strong>{{ summary.appointment_count }}</strong><span>Randevu</span></div>
            <div><strong>{{ summary.completed_appointments }}</strong><span>Tamamlanan</span></div>
            <div><strong>{{ summary.cancelled_appointments }}</strong><span>İptal</span></div>
            <div><strong>{{ summary.delivered_jobs }}</strong><span>Teslim</span></div>
          </div>
          <div class="status-list">
            <div v-for="item in jobStatuses" :key="item.status"><span>{{ item.label }}</span><strong>{{ item.count }}</strong></div>
          </div>
        </section>
      </div>

      <div class="grid three">
        <section class="panel">
          <div class="panel-title"><div><h2>En Çok Kazandıran Hizmetler</h2><span>İlk 10</span></div></div>
          <div v-if="!services.length" class="empty small">Veri bulunmuyor.</div>
          <div v-else class="rank-list">
            <div v-for="(item,index) in services" :key="item.id" class="rank-row"><b>{{ index + 1 }}</b><div class="rank-main"><strong>{{ item.name }}</strong><span>{{ number(item.quantity) }} adet</span><div class="mini-track"><i :style="{width: `${ratio(item.revenue, maxServiceRevenue)}%`}"></i></div></div><strong>{{ money(item.revenue) }}</strong></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-title"><div><h2>Market Ürünleri</h2><span>En yüksek satış cirosu</span></div></div>
          <div v-if="!products.length" class="empty small">Veri bulunmuyor.</div>
          <div v-else class="rank-list"><div v-for="(item,index) in products" :key="item.id" class="rank-row"><b>{{ index + 1 }}</b><div class="rank-main"><strong>{{ item.name }}</strong><span>{{ number(item.quantity) }} {{ item.unit }}</span><div class="mini-track"><i :style="{width: `${ratio(item.revenue, maxProductRevenue)}%`}"></i></div></div><strong>{{ money(item.revenue) }}</strong></div></div>
        </section>

        <section class="panel">
          <div class="panel-title"><div><h2>Ödeme Dağılımı</h2><span>Satış yöntemleri</span></div></div>
          <div v-if="!payments.length" class="empty small">Veri bulunmuyor.</div>
          <div v-else class="payment-list"><div v-for="item in payments" :key="item.method" class="payment-row"><span>{{ paymentLabel(item.method) }}</span><strong>{{ money(item.revenue) }}</strong><small>{{ item.count }} satış</small></div></div>
        </section>
      </div>

      <div class="grid two">
        <section class="panel">
          <div class="panel-title"><div><h2>Personel Performansı</h2><span>İş emri ve ciro</span></div></div>
          <div v-if="!staff.length" class="empty small">Bu dönemde personel verisi yok.</div>
          <table v-else><thead><tr><th>Personel</th><th>İş emri</th><th>Ciro</th></tr></thead><tbody><tr v-for="item in staff" :key="item.id"><td><strong>{{ item.name }}</strong></td><td>{{ item.jobs }}</td><td>{{ money(item.revenue) }}</td></tr></tbody></table>
        </section>
        <section class="panel highlights">
          <div class="panel-title"><div><h2>Sistem Özeti</h2><span>Genel işletme verileri</span></div></div>
          <div class="highlight-grid">
            <div><span>Toplam müşteri</span><strong>{{ summary.customer_count }}</strong></div>
            <div><span>Toplam araç</span><strong>{{ summary.vehicle_count }}</strong></div>
            <div><span>Kritik stok</span><strong>{{ summary.low_stock_count }}</strong></div>
            <div><span>Net dönem tahsilatı</span><strong>{{ money(summary.period_payments) }}</strong></div>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { getStatistics } from '../services/statistics';

const periods = [
  { key: 'today', label: 'Bugün' },
  { key: 'week', label: 'Bu Hafta' },
  { key: 'month', label: 'Bu Ay' },
  { key: 'year', label: 'Bu Yıl' },
];
const period = ref('month');
const loading = ref(false);
const error = ref('');
const data = ref({ summary: {}, daily_revenue: [], services: [], products: [], payments: [], staff: [], job_statuses: [], period: {} });

const summary = computed(() => data.value.summary || {});
const services = computed(() => data.value.services || []);
const products = computed(() => data.value.products || []);
const payments = computed(() => data.value.payments || []);
const staff = computed(() => data.value.staff || []);
const jobStatuses = computed(() => data.value.job_statuses || []);
const daily = computed(() => data.value.daily_revenue || []);
const dailyMax = computed(() => Math.max(...daily.value.map(x => Number(x.revenue) || 0), 0));
const visibleDaily = computed(() => daily.value.length > 31 ? daily.value.filter((_, i) => i % Math.ceil(daily.value.length / 31) === 0) : daily.value);
const maxServiceRevenue = computed(() => Math.max(...services.value.map(x => Number(x.revenue) || 0), 0));
const maxProductRevenue = computed(() => Math.max(...products.value.map(x => Number(x.revenue) || 0), 0));
const dateRange = computed(() => data.value.period?.start && data.value.period?.end ? `${formatDate(data.value.period.start)} — ${formatDate(data.value.period.end)}` : '');

function money(value) { return `${Number(value || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`; }
function number(value) { return Number(value || 0).toLocaleString('tr-TR', { maximumFractionDigits: 3 }); }
function formatDate(value) { return new Date(`${value}T00:00:00`).toLocaleDateString('tr-TR', { day: '2-digit', month: 'short' }); }
function ratio(value, max) { return max ? Math.max(5, Math.round((Number(value) / max) * 100)) : 0; }
function changeText(value) { const n = Number(value || 0); return `${n > 0 ? '+' : ''}${n.toLocaleString('tr-TR')}%`; }
function changeClass(value) { return Number(value || 0) >= 0 ? 'positive' : 'negative'; }
function paymentLabel(value) { return ({ cash: 'Nakit', card: 'Kart', transfer: 'Havale / EFT', other: 'Diğer', unspecified: 'Belirtilmemiş' })[value] || value; }
async function load() { loading.value = true; error.value = ''; try { data.value = await getStatistics({ period: period.value }); } catch (e) { error.value = e.message || 'İstatistikler yüklenemedi.'; } finally { loading.value = false; } }
async function setPeriod(value) { period.value = value; await load(); }
onMounted(load);
</script>

<style scoped>
.stats-page{padding:30px;max-width:1500px}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.eyebrow{font-size:11px;font-weight:800;letter-spacing:.1em;color:#128c8a;margin:0 0 6px}.page-header h1{margin:0;font-size:28px}.page-header p:last-child{margin:6px 0 0;color:#64748b}.period-actions{display:flex;gap:6px;background:#fff;border:1px solid #e4e9ef;border-radius:10px;padding:4px}.period-btn{border:0;background:transparent;padding:9px 12px;border-radius:7px;color:#64748b;font-weight:700;font-size:12px;cursor:pointer}.period-btn.active{background:#128c8a;color:#fff}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.metric{background:#fff;border:1px solid #e4e9ef;border-radius:14px;padding:19px}.metric span{font-size:12px;color:#64748b;font-weight:700}.metric strong{display:block;font-size:25px;margin:7px 0 5px}.metric small{font-size:11px;color:#94a3b8}.positive{color:#138a64!important}.negative{color:#d14b4b!important}.grid{display:grid;gap:14px;margin-top:14px}.grid.two{grid-template-columns:1.35fr 1fr}.grid.three{grid-template-columns:1.2fr 1.2fr 1fr}.panel{background:#fff;border:1px solid #e4e9ef;border-radius:14px;padding:19px;min-width:0}.panel-title{display:flex;justify-content:space-between;margin-bottom:16px}.panel-title h2{font-size:15px;margin:0}.panel-title span{font-size:11px;color:#94a3b8;display:block;margin-top:4px}.bar-chart{height:230px;display:flex;align-items:stretch;gap:7px;padding-top:12px}.bar-item{flex:1;display:flex;flex-direction:column;align-items:center;min-width:0}.bar-track{height:195px;width:100%;display:flex;align-items:flex-end;justify-content:center}.bar{width:min(24px,70%);background:#128c8a;border-radius:5px 5px 2px 2px;min-height:3px}.bar-item>span{font-size:9px;color:#94a3b8;margin-top:8px;white-space:nowrap;overflow:hidden;max-width:100%;text-overflow:ellipsis}.appointment-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.appointment-stats div{padding:13px 8px;background:#f8fafc;border-radius:9px;text-align:center}.appointment-stats strong{display:block;font-size:21px}.appointment-stats span{font-size:10px;color:#64748b}.status-list{margin-top:16px;display:grid;gap:7px}.status-list div{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eef1f5;font-size:12px}.status-list strong{font-size:12px}.rank-list{display:grid;gap:8px}.rank-row{display:flex;align-items:center;gap:9px;padding:7px 0}.rank-row>b{width:20px;text-align:center;color:#94a3b8;font-size:11px}.rank-main{flex:1;min-width:0}.rank-main strong{display:block;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.rank-main span{font-size:10px;color:#94a3b8}.rank-row>strong{font-size:11px;white-space:nowrap}.mini-track{height:4px;background:#edf1f4;border-radius:99px;margin-top:5px;overflow:hidden}.mini-track i{display:block;height:100%;background:#128c8a;border-radius:99px}.payment-list{display:grid;gap:12px}.payment-row{display:grid;grid-template-columns:1fr auto;gap:3px 8px;padding-bottom:10px;border-bottom:1px solid #eef1f5}.payment-row span{font-size:12px;font-weight:700}.payment-row strong{font-size:12px}.payment-row small{grid-column:1/-1;color:#94a3b8;font-size:10px}table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;font-size:10px;color:#94a3b8;padding:8px;border-bottom:1px solid #e9edf2}td{padding:11px 8px;border-bottom:1px solid #eef1f5}.highlight-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.highlight-grid div{background:#f8fafc;border-radius:10px;padding:14px}.highlight-grid span{display:block;font-size:10px;color:#64748b}.highlight-grid strong{display:block;font-size:20px;margin-top:5px}.empty,.loading{padding:35px;text-align:center;color:#64748b;font-size:13px}.empty.small{padding:25px}.alert{background:#fff0f0;color:#b42318;border:1px solid #ffd0d0;border-radius:10px;padding:11px 13px;margin-bottom:14px;font-size:12px}@media(max-width:1100px){.summary-grid{grid-template-columns:1fr 1fr}.grid.three{grid-template-columns:1fr 1fr}.grid.three .panel:last-child{grid-column:1/-1}}@media(max-width:800px){.page-header{display:block}.period-actions{margin-top:14px;overflow:auto}.grid.two,.grid.three{grid-template-columns:1fr}.grid.three .panel:last-child{grid-column:auto}.stats-page{padding:18px}}@media(max-width:600px){.summary-grid{grid-template-columns:1fr 1fr}.metric strong{font-size:19px}.appointment-stats{grid-template-columns:1fr 1fr}.bar-chart{gap:3px}}
</style>
