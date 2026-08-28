<template>
  <section class="tracking-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Operasyon Yönetimi</p>
        <h1>Araç Takibi</h1>
        <p>Yıkamadaki araçların hangi aşamada olduğunu tek ekrandan takip edin.</p>
      </div>
      <div class="header-actions"><button class="secondary" @click="openAppointments">Randevulardan İşleme Al</button><button class="primary" @click="openNew">+ Yeni İş Emri</button></div>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>

    <section class="summary-grid">
      <div v-for="card in summaryCards" :key="card.status" class="summary-card">
        <span>{{ card.label }}</span><strong>{{ countStatus(card.status) }}</strong><small>{{ card.hint }}</small>
      </div>
    </section>

    <div class="toolbar-card">
      <div class="date-navigation">
        <button class="icon-button" @click="moveDate(-1)">‹</button>
        <button class="today-button" @click="goToday">Bugün</button>
        <input v-model="selectedDate" type="date" @change="loadJobs" />
        <button class="icon-button" @click="moveDate(1)">›</button>
      </div>
      <select v-model="statusFilter" @change="loadJobs">
        <option value="">Tüm durumlar</option>
        <option v-for="(label, value) in statuses" :key="value" :value="value">{{ label }}</option>
      </select>
    </div>

    <section class="board">
      <div v-if="loading" class="empty">Araçlar yükleniyor...</div>
      <div v-else-if="jobs.length === 0" class="empty">
        <strong>Bugün için araç bulunmuyor</strong>
        <span>Randevudan araç işleme alabilir veya manuel iş emri oluşturabilirsiniz.</span>
      </div>
      <div v-else class="job-grid">
        <article v-for="job in jobs" :key="job.id" class="job-card" :class="`status-${job.status}`">
          <div class="job-top">
            <div><span class="plate">{{ job.vehicle.plate }}</span><span class="vehicle-name">{{ job.vehicle.brand }} {{ job.vehicle.model }}</span></div>
            <span class="priority" v-if="job.priority > 0">Öncelikli</span>
          </div>
          <div class="customer"><strong>{{ job.customer.name }}</strong><span>{{ job.customer.phone }}</span></div>
          <div class="services"><span v-for="service in job.services" :key="service.id">{{ service.name }}</span></div>
          <div class="meta-row">
            <span v-if="job.staff">👤 {{ job.staff.name }}</span><span v-else>👤 Personel atanmadı</span>
            <span v-if="job.estimated_end_at">Tahmini {{ time(job.estimated_end_at) }}</span>
          </div>
          <div class="status-row">
            <select :value="job.status" :disabled="job.status === 'delivered' || job.status === 'cancelled'" @change="changeStatus(job, $event.target.value)">
              <option :value="job.status">{{ statuses[job.status] }}</option>
              <option v-for="nextStatus in nextStatuses(job.status)" :key="nextStatus" :value="nextStatus">{{ statuses[nextStatus] }}</option>
            </select>
            <button @click="openHistory(job)">Geçmiş</button>
            <button v-if="job.status !== 'delivered' && job.status !== 'cancelled'" @click="openEdit(job)">Düzenle</button>
          </div>
          <div v-if="job.financial" class="financial-row">
            <span>Satış #{{ job.financial.sale_id }} · {{ money(job.financial.total_amount) }}</span>
            <button v-if="job.financial.payment_status === 'unpaid'" @click="markPaid(job)">Ödeme Al</button>
            <strong v-else>Ödendi</strong>
          </div>
          <div class="timestamps">
            <span v-if="job.check_in_at">Giriş {{ time(job.check_in_at) }}</span>
            <span v-if="job.started_at">Başlangıç {{ time(job.started_at) }}</span>
            <span v-if="job.ready_at">Hazır {{ time(job.ready_at) }}</span>
          </div>
        </article>
      </div>
    </section>

    <div v-if="modal" class="backdrop" @click.self="modal=false">
      <form class="modal" @submit.prevent="save">
        <div class="modal-head"><div><p class="eyebrow">{{ editing ? 'İş Emrini Düzenle' : 'Yeni İş Emri' }}</p><h2>{{ editing ? editing.vehicle.plate : 'Araç İşleme Alma' }}</h2></div><button type="button" class="close" @click="modal=false">×</button></div>

        <label> Müşteri *
          <select v-model.number="form.customer_id" required :disabled="!!editing">
            <option value="" disabled>Seçin</option><option v-for="c in lookups.customers" :key="c.id" :value="c.id">{{ c.name }} — {{ c.phone }}</option>
          </select>
        </label>
        <label> Araç *
          <select v-model.number="form.vehicle_id" required :disabled="!!editing">
            <option value="" disabled>Seçin</option><option v-for="v in customerVehicles" :key="v.id" :value="v.id">{{ v.plate }} — {{ v.brand }} {{ v.model }}</option>
          </select>
        </label>
        <div class="grid2"><label>Personel<select v-model.number="form.staff_id"><option value="">Atanmadı</option><option v-for="s in lookups.staff" :key="s.id" :value="s.id">{{ s.name }}{{ s.role ? ` — ${s.role}` : '' }}</option></select></label><label>Öncelik<select v-model.number="form.priority"><option :value="0">Normal</option><option :value="1">Öncelikli</option><option :value="2">Çok öncelikli</option></select></label></div>
        <label>Hizmetler *</label>
        <div class="service-list"><label v-for="service in lookups.services" :key="service.id" class="service-option"><input v-model="form.service_ids" :value="service.id" type="checkbox" /><span>{{ service.name }}<small>{{ money(service.price) }} · {{ service.duration_minutes }} dk</small></span></label></div>
        <div class="form-total"><span>Toplam süre: <strong>{{ selectedDuration }} dk</strong></span><span>Toplam: <strong>{{ money(selectedPrice) }}</strong></span></div>
        <label>Not<textarea v-model="form.notes" rows="3" placeholder="Araçla veya işlemle ilgili not..." /></label>
        <div v-if="error" class="alert">{{ error }}</div>
        <div class="modal-actions"><button type="button" @click="modal=false">Vazgeç</button><button class="primary" :disabled="saving">{{ saving ? 'Kaydediliyor...' : 'Kaydet' }}</button></div>
      </form>
    </div>

    <div v-if="appointmentModal" class="backdrop" @click.self="appointmentModal=false">
      <section class="appointment-modal">
        <div class="modal-head"><div><p class="eyebrow">Randevu Kuyruğu</p><h2>{{ selectedDate }}</h2></div><button class="close" @click="appointmentModal=false">×</button></div>
        <div v-if="appointmentLoading" class="empty">Randevular yükleniyor...</div>
        <div v-else-if="availableAppointments.length === 0" class="empty"><strong>İşleme alınacak randevu yok</strong><span>Bu tarihte henüz araca dönüştürülmemiş randevu bulunmuyor.</span></div>
        <div v-else class="appointment-list"><article v-for="appointment in availableAppointments" :key="appointment.id" class="appointment-item"><div><strong>{{ time(appointment.start_at) }} · {{ appointment.vehicle.plate }}</strong><span>{{ appointment.customer.name }} · {{ appointment.vehicle.brand }} {{ appointment.vehicle.model }}</span><small>{{ appointment.services.map(s => s.name).join(' · ') }}</small></div><button class="primary" @click="startAppointment(appointment.id)">İşleme Al</button></article></div>
      </section>
    </div>

    <div v-if="historyModal" class="backdrop" @click.self="historyModal=false">
      <section class="history-modal">
        <div class="modal-head"><div><p class="eyebrow">İşlem Geçmişi</p><h2>{{ historyJob?.vehicle.plate }}</h2></div><button class="close" @click="historyModal=false">×</button></div>
        <div v-if="historyLoading" class="empty">Geçmiş yükleniyor...</div>
        <div v-else class="timeline"><div v-for="item in history" :key="item.id" class="timeline-item"><div class="dot"></div><div><strong>{{ item.status_label }}</strong><span>{{ dateTime(item.changed_at) }}</span><small v-if="item.note">{{ item.note }}</small></div></div></div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { createVehicleJob, createVehicleJobFromAppointment, getAvailableAppointments, getVehicleJobHistory, getVehicleTrackingLookups, getVehicleJobs, markVehicleJobPaid, updateVehicleJob, updateVehicleJobStatus } from "../services/vehicleTracking";

const route = useRoute();
const today = new Date().toISOString().slice(0, 10);
const selectedDate = ref(today), statusFilter = ref(""), jobs = ref([]), loading = ref(false), error = ref(""), saving = ref(false);
const modal = ref(false), editing = ref(null), appointmentModal = ref(false), appointmentLoading = ref(false), availableAppointments = ref([]), historyModal = ref(false), historyJob = ref(null), history = ref([]), historyLoading = ref(false);
const lookups = reactive({ customers: [], vehicles: [], services: [], staff: [] });
const statuses = { waiting: "Bekliyor", checked_in: "İşleme Alındı", washing: "Yıkamada", quality_check: "Kontrol", ready: "Hazır", delivered: "Teslim Edildi", cancelled: "İptal" };
const transitions = { waiting: ["checked_in", "cancelled"], checked_in: ["washing", "cancelled"], washing: ["quality_check", "cancelled"], quality_check: ["ready", "washing", "cancelled"], ready: ["delivered", "washing"], delivered: [], cancelled: [] };
const summaryCards = [
  { status: "waiting", label: "Bekleyen", hint: "Sırada" }, { status: "checked_in", label: "İşleme Alınan", hint: "Başlamaya hazır" }, { status: "washing", label: "Yıkamada", hint: "Aktif işlem" }, { status: "ready", label: "Hazır", hint: "Teslim bekliyor" },
];
const form = reactive({ customer_id: "", vehicle_id: "", staff_id: "", priority: 0, service_ids: [], notes: "" });
const customerVehicles = computed(() => lookups.vehicles.filter(v => v.customer_id === Number(form.customer_id)));
const selectedServices = computed(() => lookups.services.filter(s => form.service_ids.includes(s.id)));
const selectedDuration = computed(() => selectedServices.value.reduce((sum, s) => sum + Number(s.duration_minutes), 0));
const selectedPrice = computed(() => selectedServices.value.reduce((sum, s) => sum + Number(s.price), 0));
const time = value => new Date(value).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
const dateTime = value => new Date(value).toLocaleString("tr-TR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
const money = value => `${Number(value || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`;
const countStatus = status => jobs.value.filter(j => j.status === status).length;
const nextStatuses = status => transitions[status] || [];

function resetForm() { Object.assign(form, { customer_id: "", vehicle_id: "", staff_id: "", priority: 0, service_ids: [], notes: "" }); }
function openNew() { editing.value = null; resetForm(); error.value = ""; modal.value = true; }
function openEdit(job) { editing.value = job; Object.assign(form, { customer_id: job.customer.id, vehicle_id: job.vehicle.id, staff_id: job.staff?.id || "", priority: job.priority, service_ids: job.services.map(s => s.id), notes: job.notes }); error.value = ""; modal.value = true; }
async function loadJobs() { loading.value = true; error.value = ""; try { jobs.value = await getVehicleJobs(selectedDate.value, statusFilter.value); } catch (e) { error.value = e.message; } finally { loading.value = false; } }
function moveDate(days) { const d = new Date(`${selectedDate.value}T12:00:00`); d.setDate(d.getDate() + days); selectedDate.value = d.toISOString().slice(0, 10); loadJobs(); }
function goToday() { selectedDate.value = today; loadJobs(); }
async function save() { if (!form.service_ids.length) { error.value = "En az bir hizmet seçmelisiniz."; return; } saving.value = true; error.value = ""; try { const payload = { ...form }; if (editing.value) await updateVehicleJob(editing.value.id, payload); else await createVehicleJob(payload); modal.value = false; await loadJobs(); } catch (e) { error.value = e.message; } finally { saving.value = false; } }
async function changeStatus(job, status) { const previous = job.status; job.status = status; try { await updateVehicleJobStatus(job.id, status, job.staff?.id || null); await loadJobs(); } catch (e) { job.status = previous; error.value = e.message; } }
async function openAppointments() { appointmentModal.value = true; appointmentLoading.value = true; error.value = ""; try { availableAppointments.value = await getAvailableAppointments(selectedDate.value); } catch (e) { error.value = e.message; } finally { appointmentLoading.value = false; } }
async function startAppointment(id) { try { await createVehicleJobFromAppointment(id); appointmentModal.value = false; await loadJobs(); } catch (e) { error.value = e.message; } }
async function openHistory(job) { historyJob.value = job; history.value = []; historyModal.value = true; historyLoading.value = true; try { history.value = await getVehicleJobHistory(job.id); } catch (e) { error.value = e.message; } finally { historyLoading.value = false; } }
async function markPaid(job) {
  const method = window.prompt("Ödeme yöntemi: cash = Nakit, card = Kart, transfer = Havale/EFT, other = Diğer", "cash");
  if (!method) return;
  const normalized = method.trim().toLowerCase();
  if (!["cash", "card", "transfer", "other"].includes(normalized)) { error.value = "Geçersiz ödeme yöntemi."; return; }
  if (!confirm("Bu iş emrinin ödemesini alınmış olarak işaretlemek istiyor musunuz?")) return;
  try { await markVehicleJobPaid(job.id, normalized); job.financial.payment_status = "paid"; job.financial.payment_method = normalized; } catch (e) { error.value = e.message; }
}
onMounted(async () => {
  try {
    Object.assign(lookups, await getVehicleTrackingLookups());
    await loadJobs();
    if (route.query.new === "1") openNew();
  } catch (e) { error.value = e.message; }
});
</script>

<style scoped>
.tracking-page{padding:30px;max-width:1500px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.header-actions{display:flex;gap:8px}.secondary{border:1px solid #cfd9e4;border-radius:10px;padding:10px 14px;background:#fff;color:#334155;font-weight:750;cursor:pointer}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.primary{border:0;border-radius:10px;padding:11px 16px;background:#128c8a;color:#fff;font-weight:750;cursor:pointer}.primary:disabled{opacity:.6}.alert{padding:12px 14px;border-radius:9px;background:#fbeaea;color:#a52e2e;margin-bottom:14px}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}.summary-card{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:16px 18px}.summary-card span,.summary-card small{display:block;color:#64748b;font-size:12px}.summary-card strong{display:block;font-size:25px;margin:5px 0}.toolbar-card{display:flex;justify-content:space-between;align-items:center;background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:12px 14px;margin-bottom:14px}.date-navigation{display:flex;gap:7px;align-items:center}.icon-button,.today-button,.toolbar-card select{border:1px solid #dbe3ec;background:#fff;border-radius:9px;padding:9px 12px;cursor:pointer}.icon-button{font-size:20px;line-height:18px}.toolbar-card input{border:1px solid #dbe3ec;border-radius:9px;padding:9px 11px}.board{background:#f5f7fa}.job-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.job-card{background:#fff;border:1px solid #e2e8f0;border-radius:15px;padding:17px;box-shadow:0 2px 5px rgba(15,23,42,.03)}.job-card.status-washing{border-color:#9ed9d5}.job-card.status-ready{border-color:#e5d29b}.job-top{display:flex;justify-content:space-between;align-items:flex-start}.plate{font-size:20px;font-weight:850;letter-spacing:.03em}.vehicle-name{display:block;color:#64748b;font-size:12px;margin-top:3px}.priority{font-size:10px;background:#fff1d6;color:#9a6700;padding:5px 7px;border-radius:6px;font-weight:800}.customer{display:flex;justify-content:space-between;gap:10px;margin:15px 0 10px;padding-bottom:11px;border-bottom:1px solid #edf1f5}.customer span{font-size:12px;color:#64748b}.services{display:flex;flex-wrap:wrap;gap:5px}.services span{font-size:11px;background:#f1f5f9;padding:6px 8px;border-radius:7px;color:#475569}.meta-row,.timestamps{display:flex;justify-content:space-between;gap:8px;color:#64748b;font-size:11px;margin-top:13px}.timestamps{justify-content:flex-start;flex-wrap:wrap;border-top:1px solid #edf1f5;padding-top:10px}.status-row{display:flex;gap:6px;margin-top:14px}.status-row select{flex:1;border:1px solid #dbe3ec;border-radius:8px;padding:8px;background:#fff}.status-row button{border:1px solid #dbe3ec;background:#fff;border-radius:8px;padding:8px 9px;cursor:pointer}.status-row select:disabled{background:#f8fafc;color:#64748b}.financial-row{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:10px;padding:9px 10px;border-radius:9px;background:#f8fafc;font-size:11px;color:#475569}.financial-row button{border:1px solid #b8dcd9;background:#fff;border-radius:7px;padding:6px 8px;color:#0d746f;font-weight:750;cursor:pointer}.financial-row strong{color:#16805d}.empty{text-align:center;padding:55px;color:#64748b;background:#fff;border:1px solid #e2e8f0;border-radius:15px}.empty strong,.empty span{display:block}.empty strong{color:#334155;margin-bottom:5px}.backdrop{position:fixed;inset:0;background:rgba(15,23,42,.48);display:grid;place-items:center;padding:20px;z-index:50}.appointment-modal{width:min(650px,100%);max-height:92vh;overflow:auto;background:#fff;border-radius:17px;padding:23px;display:grid;gap:14px;box-shadow:0 25px 60px rgba(0,0,0,.2)}.appointment-list{display:grid;gap:8px}.appointment-item{display:flex;justify-content:space-between;align-items:center;gap:15px;padding:13px;border:1px solid #e3e8ef;border-radius:11px}.appointment-item strong,.appointment-item span,.appointment-item small{display:block}.appointment-item span{font-size:12px;color:#64748b;margin-top:3px}.appointment-item small{font-size:11px;color:#7a8797;margin-top:5px}.modal,.history-modal{width:min(620px,100%);max-height:92vh;overflow:auto;background:#fff;border-radius:17px;padding:23px;display:grid;gap:14px;box-shadow:0 25px 60px rgba(0,0,0,.2)}.history-modal{width:min(500px,100%)}.modal-head{display:flex;justify-content:space-between;align-items:flex-start}.modal-head h2{margin:4px 0 0}.close{border:0;background:transparent;font-size:27px;cursor:pointer;color:#64748b}.modal label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155}.modal input,.modal select,.modal textarea{width:100%;box-sizing:border-box;border:1px solid #d8e0e8;border-radius:9px;padding:10px 11px;background:#fff}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.service-list{border:1px solid #e1e7ee;border-radius:10px;overflow:hidden}.service-option{display:flex!important;flex-direction:row;align-items:center;gap:10px!important;padding:10px 12px;border-bottom:1px solid #edf1f5;cursor:pointer}.service-option:last-child{border:0}.service-option input{width:auto}.service-option span{display:flex;justify-content:space-between;gap:15px;width:100%}.service-option small{color:#64748b;font-weight:500}.form-total{display:flex;justify-content:space-between;color:#64748b}.form-total strong{color:#0d746f}.modal-actions{display:flex;justify-content:flex-end;gap:8px}.modal-actions button:not(.primary){border:1px solid #dbe3ec;background:#fff;border-radius:9px;padding:10px 14px;cursor:pointer}.timeline{display:grid;gap:0}.timeline-item{display:grid;grid-template-columns:22px 1fr;gap:10px;position:relative;padding-bottom:18px}.timeline-item:not(:last-child):after{content:"";position:absolute;left:7px;top:14px;bottom:0;width:1px;background:#dbe3ec}.dot{width:15px;height:15px;border-radius:50%;background:#128c8a;margin-top:2px;z-index:1}.timeline-item strong,.timeline-item span,.timeline-item small{display:block}.timeline-item span{font-size:11px;color:#64748b;margin-top:3px}.timeline-item small{font-size:12px;color:#475569;margin-top:5px}@media(max-width:1100px){.job-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.summary-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:720px){.tracking-page{padding:18px}.page-header,.toolbar-card{align-items:flex-start;flex-direction:column}.header-actions{width:100%;flex-direction:column}.header-actions button{width:100%}.summary-grid,.job-grid{grid-template-columns:1fr}.grid2{grid-template-columns:1fr}.date-navigation{flex-wrap:wrap}.status-row{flex-wrap:wrap}.status-row select{min-width:100%}}
</style>
