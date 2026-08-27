<template>
  <div class="appointment-page">
    <header class="page-header">
      <div><p class="eyebrow">Yönetim</p><h1>Randevu Yönetimi</h1><p>Günün randevularını takip edin ve yeni randevu oluşturun.</p></div>
      <div class="actions"><input v-model="selectedDate" type="date" @change="load" /><button class="primary" @click="openNew">+ Yeni Randevu</button></div>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <section class="schedule-card">
      <div class="schedule-head"><strong>{{ formattedDate }}</strong><span>{{ appointments.length }} randevu</span></div>
      <div v-if="loading" class="empty">Yükleniyor...</div>
      <div v-else-if="!appointments.length" class="empty">Bu tarih için randevu bulunmuyor.</div>
      <div v-else class="appointments">
        <article v-for="item in appointments" :key="item.id" class="appointment-row">
          <div class="time"><strong>{{ time(item.start_at) }}</strong><small>{{ time(item.end_at) }}</small></div>
          <div class="vehicle"><strong>{{ item.vehicle.plate }}</strong><span>{{ item.vehicle.brand }} {{ item.vehicle.model }}</span></div>
          <div><strong>{{ item.customer.name }}</strong><span>{{ item.customer.phone }}</span></div>
          <div><strong>{{ item.services.map(s => s.name).join(', ') }}</strong><span>{{ item.services.reduce((t, s) => t + s.duration_minutes, 0) }} dk</span></div>
          <span :class="['status', item.status]">{{ statusLabel(item.status) }}</span>
          <div class="row-actions"><button @click="openEdit(item)">Düzenle</button><button class="danger" @click="cancel(item.id)">İptal</button></div>
        </article>
      </div>
    </section>

    <div v-if="modal" class="modal-backdrop" @click.self="modal=false">
      <form class="modal" @submit.prevent="save">
        <div class="modal-head"><h2>{{ editing ? 'Randevuyu Düzenle' : 'Yeni Randevu' }}</h2><button type="button" @click="modal=false">×</button></div>
        <label>Tarih <input v-model="form.date" type="date" required /></label>
        <label>Saat <input v-model="form.time" type="time" required /></label>
        <label>Müşteri <select v-model.number="form.customer_id" required><option disabled value="">Seçin</option><option v-for="c in lookups.customers" :value="c.id" :key="c.id">{{ c.name }} — {{ c.phone }}</option></select></label>
        <label>Araç <select v-model.number="form.vehicle_id" required><option disabled value="">Seçin</option><option v-for="v in customerVehicles" :value="v.id" :key="v.id">{{ v.plate }} — {{ v.brand }} {{ v.model }}</option></select></label>
        <label>Hizmet <select v-model.number="form.service_id" required><option disabled value="">Seçin</option><option v-for="s in lookups.services" :value="s.id" :key="s.id">{{ s.name }} — {{ s.duration_minutes }} dk / {{ s.price }} TL</option></select></label>
        <label>Durum <select v-model="form.status"><option value="scheduled">Planlandı</option><option value="arrived">Geldi</option><option value="in_service">İşlemde</option><option value="completed">Tamamlandı</option><option value="cancelled">İptal</option></select></label>
        <label>Not <textarea v-model="form.notes" rows="3"></textarea></label>
        <div class="modal-actions"><button type="button" @click="modal=false">Vazgeç</button><button class="primary" type="submit" :disabled="saving">{{ saving ? 'Kaydediliyor...' : 'Kaydet' }}</button></div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { cancelAppointment, createAppointment, getAppointmentLookups, getAppointments, updateAppointment } from "../services/appointments";

const today = new Date().toISOString().slice(0, 10);
const selectedDate = ref(today), appointments = ref([]), lookups = reactive({ customers: [], vehicles: [], services: [] });
const modal = ref(false), editing = ref(null), loading = ref(false), saving = ref(false), error = ref("");
const form = reactive({ date: today, time: "09:00", customer_id: "", vehicle_id: "", service_id: "", status: "scheduled", notes: "" });
const formattedDate = computed(() => new Date(`${selectedDate.value}T12:00:00`).toLocaleDateString("tr-TR", { weekday: "long", day: "numeric", month: "long", year: "numeric" }));
const customerVehicles = computed(() => lookups.vehicles.filter(v => v.customer_id === Number(form.customer_id)));
const time = value => new Date(value).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
const statusLabel = s => ({ scheduled: "Planlandı", arrived: "Geldi", in_service: "İşlemde", completed: "Tamamlandı", cancelled: "İptal" }[s] || s);

async function load() { loading.value = true; error.value = ""; try { appointments.value = await getAppointments(selectedDate.value); } catch (e) { error.value = e.message; } finally { loading.value = false; } }
function resetForm() { Object.assign(form, { date: selectedDate.value, time: "09:00", customer_id: "", vehicle_id: "", service_id: "", status: "scheduled", notes: "" }); }
function openNew() { editing.value = null; resetForm(); modal.value = true; }
function openEdit(item) { editing.value = item; Object.assign(form, { date: item.start_at.slice(0,10), time: time(item.start_at), customer_id: item.customer.id, vehicle_id: item.vehicle.id, service_id: item.services[0]?.id || "", status: item.status, notes: item.notes }); modal.value = true; }
async function save() { saving.value = true; error.value = ""; try { const payload = { customer_id: form.customer_id, vehicle_id: form.vehicle_id, service_ids: [form.service_id], start_at: `${form.date}T${form.time}`, status: form.status, notes: form.notes }; if (editing.value) await updateAppointment(editing.value.id, payload); else await createAppointment(payload); modal.value = false; selectedDate.value = form.date; await load(); } catch (e) { error.value = e.message; } finally { saving.value = false; } }
async function cancel(id) { if (!confirm("Bu randevuyu iptal etmek istediğinize emin misiniz?")) return; try { await cancelAppointment(id); await load(); } catch (e) { error.value = e.message; } }
onMounted(async () => { try { Object.assign(lookups, await getAppointmentLookups()); await load(); } catch (e) { error.value = e.message; } });
</script>

<style scoped>
.appointment-page{padding:28px;max-width:1500px;margin:auto}.page-header{display:flex;justify-content:space-between;gap:20px;align-items:flex-end;margin-bottom:24px}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:12px;font-weight:800;letter-spacing:.08em}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.actions{display:flex;gap:10px;align-items:center}.actions input,.modal input,.modal select,.modal textarea{border:1px solid #dbe3ec;border-radius:10px;padding:10px;background:#fff}.primary{border:0;border-radius:10px;padding:11px 16px;background:#128c8a;color:white;font-weight:700;cursor:pointer}.schedule-card{background:white;border:1px solid #e2e8f0;border-radius:16px;overflow:hidden}.schedule-head{padding:18px 20px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between}.schedule-head span,.appointment-row span{color:#64748b;font-size:13px}.appointments{display:grid}.appointment-row{display:grid;grid-template-columns:90px 1.1fr 1fr 1.4fr 110px 150px;gap:16px;align-items:center;padding:17px 20px;border-bottom:1px solid #edf2f7}.appointment-row:last-child{border:0}.appointment-row strong,.appointment-row span{display:block}.time small{color:#94a3b8}.status{padding:6px 10px;border-radius:999px;text-align:center;font-weight:700;background:#eef2f6}.status.scheduled{background:#e7f6f4;color:#0f766e}.status.arrived,.status.in_service{background:#fff4dc;color:#9a6500}.status.completed{background:#e9f7ef;color:#18794e}.status.cancelled{background:#fbeaea;color:#b33434}.row-actions{display:flex;gap:6px}.row-actions button,.modal-actions button{border:1px solid #dbe3ec;background:white;border-radius:8px;padding:8px 10px;cursor:pointer}.row-actions .danger{color:#b33434}.empty{padding:50px;text-align:center;color:#64748b}.alert{margin-bottom:16px;padding:12px 14px;border-radius:10px;background:#fbeaea;color:#a62b2b}.modal-backdrop{position:fixed;inset:0;background:rgba(15,23,42,.45);display:grid;place-items:center;padding:20px}.modal{width:min(520px,100%);background:white;border-radius:16px;padding:22px;display:grid;gap:14px;box-shadow:0 20px 50px rgba(0,0,0,.18)}.modal-head{display:flex;justify-content:space-between;align-items:center}.modal-head h2{margin:0}.modal-head button{border:0;background:transparent;font-size:26px;cursor:pointer}.modal label{display:grid;gap:6px;font-size:13px;font-weight:700}.modal-actions{display:flex;justify-content:flex-end;gap:8px}@media(max-width:1000px){.appointment-row{grid-template-columns:80px 1fr 1fr}.appointment-row>:nth-child(4),.appointment-row .row-actions{grid-column:2}.page-header{align-items:flex-start;flex-direction:column}}
</style>
