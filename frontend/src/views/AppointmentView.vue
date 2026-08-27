<template>
  <section class="appointment-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Yönetim</p>
        <h1>Randevu Yönetimi</h1>
        <p>Randevuları hızlıca planlayın, takip edin ve durumlarını yönetin.</p>
      </div>
      <button class="primary" @click="openNew">+ Yeni Randevu</button>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>

    <section class="toolbar-card">
      <div class="date-navigation">
        <button class="icon-button" @click="moveDate(-1)" aria-label="Önceki gün">‹</button>
        <input v-model="selectedDate" type="date" @change="loadAppointments" />
        <button class="today-button" @click="goToday">Bugün</button>
        <button class="icon-button" @click="moveDate(1)" aria-label="Sonraki gün">›</button>
      </div>
      <div class="view-tabs">
        <button :class="{ active: viewMode === 'day' }" @click="viewMode = 'day'">Günlük</button>
        <button :class="{ active: viewMode === 'week' }" @click="viewMode = 'week'">Haftalık</button>
      </div>
    </section>

    <section class="summary-grid">
      <div class="summary-card"><span>Toplam Randevu</span><strong>{{ appointments.length }}</strong></div>
      <div class="summary-card"><span>Planlandı</span><strong>{{ countStatus('scheduled') }}</strong></div>
      <div class="summary-card"><span>İşlemde</span><strong>{{ countStatus('in_service') }}</strong></div>
      <div class="summary-card"><span>Günlük Hizmet Değeri</span><strong>{{ money(dayRevenue) }}</strong></div>
    </section>

    <section v-if="viewMode === 'week'" class="week-grid">
      <button
        v-for="day in weekDays"
        :key="day.date"
        class="week-day"
        :class="{ selected: day.date === selectedDate }"
        @click="selectedDate = day.date; viewMode = 'day'; loadAppointments()"
      >
        <span>{{ day.label }}</span><strong>{{ day.day }}</strong><small>{{ day.count }} randevu</small>
      </button>
    </section>

    <section class="schedule-card">
      <div class="schedule-head">
        <div><strong>{{ formattedDate }}</strong><span>{{ appointments.length }} randevu</span></div>
        <select v-model="statusFilter" @change="loadAppointments">
          <option value="">Tüm durumlar</option>
          <option value="scheduled">Planlandı</option>
          <option value="arrived">Geldi</option>
          <option value="in_service">İşlemde</option>
          <option value="completed">Tamamlandı</option>
          <option value="cancelled">İptal</option>
        </select>
      </div>

      <div v-if="loading" class="empty">Randevular yükleniyor...</div>
      <div v-else-if="!appointments.length" class="empty">
        <strong>Bu tarih için randevu yok.</strong>
        <span>Yeni bir randevu oluşturarak takvimi doldurabilirsiniz.</span>
      </div>

      <div v-else class="appointments">
        <article v-for="item in appointments" :key="item.id" class="appointment-row">
          <div class="time"><strong>{{ time(item.start_at) }}</strong><small>{{ time(item.end_at) }}</small></div>
          <div class="main-info">
            <strong>{{ item.vehicle.plate }}</strong>
            <span>{{ item.vehicle.brand }} {{ item.vehicle.model }}</span>
          </div>
          <div class="main-info">
            <strong>{{ item.customer.name }}</strong>
            <span>{{ item.customer.phone }}</span>
          </div>
          <div class="main-info services">
            <strong>{{ item.services.map(s => s.name).join(' + ') }}</strong>
            <span>{{ item.total_duration_minutes }} dk · {{ money(item.total_price) }}</span>
          </div>
          <select class="status-select" :value="item.status" @change="changeStatus(item, $event.target.value)">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
          <div class="row-actions">
            <button @click="openEdit(item)">Düzenle</button>
            <button class="danger" @click="cancel(item.id)">İptal</button>
          </div>
        </article>
      </div>
    </section>

    <div v-if="modal" class="modal-backdrop" @click.self="modal = false">
      <form class="modal" @submit.prevent="save">
        <div class="modal-head"><div><p class="eyebrow">Randevu</p><h2>{{ editing ? 'Randevuyu Düzenle' : 'Yeni Randevu' }}</h2></div><button type="button" class="close" @click="modal = false">×</button></div>

        <div class="grid2">
          <label>Tarih *<input v-model="form.date" type="date" required /></label>
          <label>Saat *<input v-model="form.time" type="time" required /></label>
        </div>

        <label>Müşteri *
          <select v-model.number="form.customer_id" required @change="form.vehicle_id = ''">
            <option value="" disabled>Seçin</option>
            <option v-for="c in lookups.customers" :key="c.id" :value="c.id">{{ c.name }} — {{ c.phone }}</option>
          </select>
        </label>

        <label>Araç *
          <select v-model.number="form.vehicle_id" required :disabled="!form.customer_id">
            <option value="" disabled>{{ form.customer_id ? 'Araç seçin' : 'Önce müşteri seçin' }}</option>
            <option v-for="v in customerVehicles" :key="v.id" :value="v.id">{{ v.plate }} — {{ v.brand }} {{ v.model }}</option>
          </select>
        </label>

        <div>
          <label>Hizmetler *</label>
          <div class="service-list">
            <label v-for="service in lookups.services" :key="service.id" class="service-option">
              <input v-model="form.service_ids" type="checkbox" :value="service.id" />
              <span><strong>{{ service.name }}</strong><small>{{ service.duration_minutes }} dk · {{ money(service.price) }}</small></span>
            </label>
          </div>
          <div class="form-total"><span>Toplam</span><strong>{{ selectedDuration }} dk · {{ money(selectedPrice) }}</strong></div>
        </div>

        <label>Durum
          <select v-model="form.status">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </label>
        <label>Not<textarea v-model="form.notes" rows="3" placeholder="Müşterinin özel talebi, araç notu vb."></textarea></label>

        <div class="modal-actions"><button type="button" @click="modal = false">Vazgeç</button><button class="primary" type="submit" :disabled="saving">{{ saving ? 'Kaydediliyor...' : 'Randevuyu Kaydet' }}</button></div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { cancelAppointment, createAppointment, getAppointmentLookups, getAppointments, updateAppointment, updateAppointmentStatus } from "../services/appointments";

const today = new Date().toISOString().slice(0, 10);
const selectedDate = ref(today);
const viewMode = ref("day");
const statusFilter = ref("");
const appointments = ref([]);
const weekAppointments = ref({});
const lookups = reactive({ customers: [], vehicles: [], services: [] });
const modal = ref(false), editing = ref(null), loading = ref(false), saving = ref(false), error = ref("");
const form = reactive({ date: today, time: "09:00", customer_id: "", vehicle_id: "", service_ids: [], status: "scheduled", notes: "" });

const statusOptions = [
  { value: "scheduled", label: "Planlandı" },
  { value: "arrived", label: "Geldi" },
  { value: "in_service", label: "İşlemde" },
  { value: "completed", label: "Tamamlandı" },
  { value: "cancelled", label: "İptal" },
];

const formattedDate = computed(() => new Date(`${selectedDate.value}T12:00:00`).toLocaleDateString("tr-TR", { weekday: "long", day: "numeric", month: "long", year: "numeric" }));
const customerVehicles = computed(() => lookups.vehicles.filter(v => v.customer_id === Number(form.customer_id)));
const selectedServices = computed(() => lookups.services.filter(s => form.service_ids.includes(s.id)));
const selectedDuration = computed(() => selectedServices.value.reduce((total, service) => total + Number(service.duration_minutes), 0));
const selectedPrice = computed(() => selectedServices.value.reduce((total, service) => total + Number(service.price), 0));
const dayRevenue = computed(() => appointments.value.filter(a => a.status !== "cancelled").reduce((sum, a) => sum + Number(a.total_price || 0), 0));
const weekDays = computed(() => {
  const date = new Date(`${selectedDate.value}T12:00:00`);
  const mondayOffset = (date.getDay() + 6) % 7;
  date.setDate(date.getDate() - mondayOffset);
  return Array.from({ length: 7 }, (_, index) => {
    const d = new Date(date); d.setDate(date.getDate() + index);
    const iso = d.toISOString().slice(0, 10);
    return { date: iso, day: d.getDate(), label: d.toLocaleDateString("tr-TR", { weekday: "short" }), count: (weekAppointments.value[iso] || []).length };
  });
});

const time = value => new Date(value).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
const money = value => `${Number(value || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`;
const countStatus = status => appointments.value.filter(a => a.status === status).length;

function resetForm() { Object.assign(form, { date: selectedDate.value, time: "09:00", customer_id: "", vehicle_id: "", service_ids: [], status: "scheduled", notes: "" }); }
function openNew() { editing.value = null; resetForm(); error.value = ""; modal.value = true; }
function openEdit(item) { editing.value = item; Object.assign(form, { date: item.start_at.slice(0, 10), time: time(item.start_at), customer_id: item.customer.id, vehicle_id: item.vehicle.id, service_ids: item.services.map(s => s.id), status: item.status, notes: item.notes }); error.value = ""; modal.value = true; }
function moveDate(days) { const d = new Date(`${selectedDate.value}T12:00:00`); d.setDate(d.getDate() + days); selectedDate.value = d.toISOString().slice(0, 10); loadAppointments(); }
function goToday() { selectedDate.value = today; loadAppointments(); }

async function loadAppointments() {
  loading.value = true; error.value = "";
  try { appointments.value = await getAppointments(selectedDate.value, statusFilter.value); }
  catch (e) { error.value = e.message; }
  finally { loading.value = false; }
  if (viewMode.value === "week") await loadWeek();
}

async function loadWeek() {
  const days = weekDays.value;
  const results = await Promise.all(days.map(day => getAppointments(day.date).catch(() => [])));
  weekAppointments.value = Object.fromEntries(days.map((day, index) => [day.date, results[index]]));
}

async function save() {
  if (!form.service_ids.length) { error.value = "En az bir hizmet seçmelisiniz."; return; }
  saving.value = true; error.value = "";
  try {
    const payload = { customer_id: form.customer_id, vehicle_id: form.vehicle_id, service_ids: form.service_ids, start_at: `${form.date}T${form.time}`, status: form.status, notes: form.notes };
    if (editing.value) await updateAppointment(editing.value.id, payload); else await createAppointment(payload);
    modal.value = false; selectedDate.value = form.date; await loadAppointments();
  } catch (e) { error.value = e.message; }
  finally { saving.value = false; }
}

async function changeStatus(item, status) {
  const oldStatus = item.status;
  item.status = status;
  try { await updateAppointmentStatus(item.id, status); }
  catch (e) { item.status = oldStatus; error.value = e.message; }
}

async function cancel(id) {
  if (!confirm("Bu randevuyu iptal etmek istediğinize emin misiniz?")) return;
  try { await cancelAppointment(id); await loadAppointments(); } catch (e) { error.value = e.message; }
}

onMounted(async () => {
  try { Object.assign(lookups, await getAppointmentLookups()); await loadAppointments(); }
  catch (e) { error.value = e.message; }
});
</script>

<style scoped>
.appointment-page{padding:30px;max-width:1500px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.primary{border:0;border-radius:10px;padding:11px 16px;background:#128c8a;color:#fff;font-weight:750;cursor:pointer}.primary:disabled{opacity:.6;cursor:not-allowed}.toolbar-card{display:flex;justify-content:space-between;align-items:center;gap:16px;background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:12px 14px;margin-bottom:14px}.date-navigation,.view-tabs{display:flex;align-items:center;gap:7px}.date-navigation input{border:1px solid #dbe3ec;border-radius:9px;padding:9px 11px}.icon-button,.today-button,.view-tabs button{border:1px solid #dbe3ec;background:#fff;border-radius:9px;padding:9px 12px;cursor:pointer}.icon-button{font-size:20px;line-height:18px}.view-tabs button.active{background:#e8f7f5;border-color:#a9ded9;color:#0d746f;font-weight:700}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}.summary-card{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:17px 18px}.summary-card span{display:block;color:#64748b;font-size:12px}.summary-card strong{display:block;font-size:23px;margin-top:5px}.week-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;margin-bottom:14px}.week-day{border:1px solid #e2e8f0;background:#fff;border-radius:12px;padding:12px;text-align:left;cursor:pointer}.week-day span,.week-day small{display:block;color:#64748b;font-size:11px}.week-day strong{display:block;font-size:21px;margin:3px 0}.week-day.selected{border-color:#8ccfca;background:#edf9f7}.schedule-card{background:#fff;border:1px solid #e2e8f0;border-radius:15px;overflow:hidden}.schedule-head{padding:16px 18px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;gap:15px}.schedule-head strong,.schedule-head span{display:block}.schedule-head span{font-size:12px;color:#64748b;margin-top:3px}.schedule-head select,.status-select{border:1px solid #dbe3ec;border-radius:8px;background:#fff;padding:8px}.appointments{display:grid}.appointment-row{display:grid;grid-template-columns:85px 1fr 1fr 1.45fr 130px 145px;gap:15px;align-items:center;padding:16px 18px;border-bottom:1px solid #edf2f7}.appointment-row:last-child{border:0}.time strong,.main-info strong{display:block}.time small,.main-info span{display:block;color:#64748b;font-size:12px;margin-top:3px}.services strong{white-space:normal}.row-actions{display:flex;gap:6px}.row-actions button{border:1px solid #dbe3ec;background:#fff;border-radius:8px;padding:8px 9px;cursor:pointer}.row-actions .danger{color:#b33434}.empty{text-align:center;padding:55px;color:#64748b}.empty strong,.empty span{display:block}.empty strong{color:#334155;margin-bottom:5px}.alert{margin-bottom:14px;padding:12px 14px;border-radius:9px;background:#fbeaea;color:#a52e2e}.modal-backdrop{position:fixed;inset:0;background:rgba(15,23,42,.48);display:grid;place-items:center;padding:20px;z-index:50}.modal{width:min(620px,100%);max-height:92vh;overflow:auto;background:#fff;border-radius:17px;padding:23px;display:grid;gap:14px;box-shadow:0 25px 60px rgba(0,0,0,.2)}.modal-head{display:flex;justify-content:space-between;align-items:flex-start}.modal-head h2{margin:4px 0 0}.close{border:0;background:transparent;font-size:27px;cursor:pointer;color:#64748b}.modal label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155}.modal input,.modal select,.modal textarea{width:100%;box-sizing:border-box;border:1px solid #d8e0e8;border-radius:9px;padding:10px 11px;background:#fff}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.service-list{border:1px solid #e1e7ee;border-radius:10px;overflow:hidden;margin-top:7px}.service-option{display:flex!important;grid-template-columns:none!important;flex-direction:row;align-items:center;gap:10px!important;padding:10px 12px;border-bottom:1px solid #edf1f5;cursor:pointer}.service-option:last-child{border-bottom:0}.service-option input{width:auto}.service-option span{display:flex;justify-content:space-between;gap:15px;align-items:center;width:100%}.service-option small{color:#64748b;font-weight:500}.form-total{display:flex;justify-content:space-between;padding:11px 2px 0;color:#64748b}.form-total strong{color:#0d746f}.modal-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:4px}.modal-actions button:not(.primary){border:1px solid #dbe3ec;background:#fff;border-radius:9px;padding:10px 14px;cursor:pointer}@media(max-width:1100px){.appointment-row{grid-template-columns:80px 1fr 1fr}.appointment-row .services,.appointment-row .status-select,.appointment-row .row-actions{grid-column:2 / -1}.summary-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:720px){.appointment-page{padding:18px}.page-header,.toolbar-card{align-items:flex-start;flex-direction:column}.summary-grid{grid-template-columns:1fr}.week-grid{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}.appointment-row{grid-template-columns:70px 1fr}.appointment-row>:nth-child(n+3){grid-column:2}.service-option span{align-items:flex-start;flex-direction:column;gap:2px}}
</style>
