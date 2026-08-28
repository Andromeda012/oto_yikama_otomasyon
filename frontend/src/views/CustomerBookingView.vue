<template>
  <main class="customer-page">
    <header class="customer-top"><RouterLink to="/" class="back">‹</RouterLink><div><strong>Randevu Al</strong><small>Online randevu</small></div><span></span></header>
    <div class="content">
      <div class="steps"><span :class="{active: step===1}">1</span><i></i><span :class="{active: step===2}">2</span></div>

      <section v-if="step === 1" class="card">
        <p class="eyebrow">HİZMET VE BİLGİLER</p><h1>Randevunuzu oluşturun</h1>
        <p class="muted">İsterseniz önce Hesabım bölümünden bilgilerinizi kaydedebilirsiniz. Hesap oluşturmak zorunlu değildir.</p>

        <div class="service-grid">
          <button v-for="service in services" :key="service.id" type="button" class="service-card" :class="{selected:selectedServiceId===service.id}" @click="selectedServiceId=service.id">
            <span class="radio">{{ selectedServiceId===service.id ? '✓' : '' }}</span>
            <div><strong>{{ service.name }}</strong><small>{{ service.duration_minutes }} dk · {{ money(service.price) }}</small><p v-if="service.description">{{ service.description }}</p></div>
          </button>
        </div>
        <div v-if="loadingServices" class="loading">Hizmetler yükleniyor…</div>

        <p class="eyebrow section-label">KİŞİ BİLGİLERİ</p>
        <label>Ad<input v-model="form.first_name" placeholder="Adınız" autocomplete="given-name"></label>
        <label>Soyad<input v-model="form.last_name" placeholder="Soyadınız" autocomplete="family-name"></label>
        <label>Telefon<input v-model="form.phone" type="tel" placeholder="05xx xxx xx xx" autocomplete="tel"></label>
        <p class="eyebrow section-label">ARAÇ BİLGİLERİ</p>
        <label>Plaka<input v-model="form.plate" placeholder="34 ABC 123" @input="form.plate = form.plate.toUpperCase()" autocomplete="off"></label>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="primary" :disabled="!validInfo || !selectedServiceId" @click="continueToSlots">Gün ve Saat Seç <span>›</span></button>
      </section>

      <section v-else class="card wide-card">
        <div class="card-head"><div><p class="eyebrow">RANDEVU ZAMANI</p><h1>Gün ve saat seçin</h1></div><button class="edit" @click="step=1">Bilgileri değiştir</button></div>
        <div class="summary"><strong>{{ selectedService?.name }}</strong><span>{{ money(selectedService?.price) }} · {{ selectedService?.duration_minutes }} dk</span><b>{{ form.first_name }} {{ form.last_name }} · {{ form.plate }}</b></div>
        <div class="date-scroller"><button v-for="day in days" :key="day.date" :class="['day', {selected:selectedDate===day.date, disabled:day.closed}]" :disabled="day.closed" @click="selectDate(day.date)"><small>{{ day.weekday }}</small><strong>{{ day.day }}</strong><span>{{ day.month }}</span></button></div>
        <div v-if="loadingSlots" class="loading">Müsait saatler yükleniyor…</div>
        <div v-else-if="slots.length" class="slot-grid"><button v-for="slot in slots" :key="slot.time" :disabled="!slot.available" :class="{selected:selectedTime===slot.time}" @click="selectedTime=slot.time"><span>{{ slot.time }}</span><small v-if="!slot.available">Dolu</small></button></div>
        <div v-else class="empty">Bu gün için uygun randevu saati bulunmuyor.</div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="primary" :disabled="!selectedTime || saving" @click="save">{{ saving ? 'Kaydediliyor…' : 'Randevuyu Kaydet' }}</button>
      </section>
    </div>
  </main>
</template>
<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { createCustomerAppointment, getAvailability, getPublicServices } from "../services/customer";
const router=useRouter();
const step=ref(1), error=ref(""), loadingSlots=ref(false), loadingServices=ref(false), saving=ref(false), selectedDate=ref(""), selectedTime=ref(""), selectedServiceId=ref(null);
const slots=ref([]), services=ref([]), form=ref({first_name:"",last_name:"",phone:"",plate:""});
const selectedService=computed(()=>services.value.find(s=>s.id===selectedServiceId.value));
const validInfo=computed(()=>form.value.first_name.trim()&&form.value.last_name.trim()&&form.value.phone.replace(/\D/g,"").length>=10&&form.value.plate.trim().length>=4);
const days=computed(()=>Array.from({length:15},(_,i)=>{const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()+i);const date=d.toISOString().slice(0,10);return {date,day:d.getDate(),month:d.toLocaleDateString("tr-TR",{month:"short"}).replace(".",""),weekday:i===0?"Bugün":d.toLocaleDateString("tr-TR",{weekday:"short"}),closed:false}}));
function money(v){return `${Number(v||0).toLocaleString("tr-TR",{minimumFractionDigits:2,maximumFractionDigits:2})} ₺`}
async function continueToSlots(){error.value="";step.value=2;if(!selectedDate.value)selectedDate.value=days.value[0].date;await loadSlots()}
async function selectDate(date){selectedDate.value=date;selectedTime.value="";await loadSlots()}
async function loadSlots(){loadingSlots.value=true;error.value="";try{const data=await getAvailability(selectedDate.value,selectedServiceId.value);slots.value=data.slots||[]}catch(e){error.value=e.message;slots.value=[]}finally{loadingSlots.value=false}}
async function save(){saving.value=true;error.value="";try{await createCustomerAppointment({first_name:form.value.first_name,last_name:form.value.last_name,phone:form.value.phone,plate:form.value.plate,service_id:selectedServiceId.value,start_at:`${selectedDate.value}T${selectedTime.value}`});sessionStorage.setItem("customer_lookup",JSON.stringify({phone:form.value.phone,plate:form.value.plate}));router.replace("/musteri/randevu-takip?success=1")}catch(e){error.value=e.message;await loadSlots()}finally{saving.value=false}}
onMounted(async()=>{selectedDate.value=days.value[0].date;loadingServices.value=true;try{const data=await getPublicServices();services.value=data.services||[];if(services.value.length)selectedServiceId.value=services.value[0].id}catch(e){error.value=e.message}finally{loadingServices.value=false};try{const saved=JSON.parse(sessionStorage.getItem("customer_profile")||"null");if(saved)form.value={...form.value,...saved}}catch{}})
</script>
<style scoped>
.customer-page{min-height:100vh;background:#f5f7fa;color:#172033;padding-bottom:35px}.customer-top{height:68px;background:#fff;border-bottom:1px solid #e6eaf0;display:grid;grid-template-columns:44px 1fr 44px;align-items:center;padding:0 18px;position:sticky;top:0;z-index:10}.customer-top strong,.customer-top small{display:block}.customer-top strong{font-size:15px}.customer-top small{font-size:10px;color:#7b8797;margin-top:2px}.back{text-decoration:none;color:#334155;font-size:30px;line-height:1}.content{max-width:700px;margin:auto;padding:22px 18px}.steps{display:flex;align-items:center;justify-content:center;margin:4px 0 20px}.steps span{width:28px;height:28px;border-radius:50%;display:grid;place-items:center;border:1px solid #d8e0e8;background:#fff;color:#94a3b8;font-size:12px;font-weight:800}.steps span.active{background:#128c8a;border-color:#128c8a;color:#fff}.steps i{width:55px;height:1px;background:#dce3eb}.card{background:#fff;border:1px solid #e1e7ee;border-radius:18px;padding:24px;box-shadow:0 10px 30px rgba(23,32,51,.04)}.eyebrow{font-size:10px;letter-spacing:.11em;font-weight:850;color:#128c8a;margin:0 0 7px}.card h1{font-size:25px;margin:0 0 7px}.muted{color:#718096;font-size:12px;line-height:1.5;margin:0 0 20px}.service-grid{display:grid;gap:9px}.service-card{display:flex;gap:12px;text-align:left;border:1px solid #dfe6ed;background:#fff;border-radius:12px;padding:13px;cursor:pointer}.service-card.selected{border-color:#73c6c0;background:#eef9f7}.radio{width:22px;height:22px;border:1px solid #cbd5df;border-radius:50%;display:grid;place-items:center;flex:none;color:#fff;font-size:12px}.selected .radio{background:#128c8a;border-color:#128c8a}.service-card strong,.service-card small,.service-card p{display:block}.service-card strong{font-size:13px}.service-card small{font-size:11px;color:#128c8a;margin-top:3px}.service-card p{font-size:10px;color:#718096;margin:5px 0 0}.card label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155;margin-top:13px}.card input{width:100%;box-sizing:border-box;border:1px solid #d8e0e8;border-radius:10px;padding:12px;outline:none;background:#fff}.card input:focus{border-color:#75c7c2;box-shadow:0 0 0 3px #e8f7f5}.section-label{margin-top:25px;margin-bottom:0}.primary{width:100%;border:0;background:#128c8a;color:#fff;border-radius:11px;padding:13px 15px;font-weight:800;cursor:pointer;margin-top:20px}.primary:disabled{opacity:.5;cursor:not-allowed}.primary span{float:right;font-size:18px}.wide-card{padding:22px}.card-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.edit{border:0;background:transparent;color:#128c8a;font-size:11px;font-weight:750;cursor:pointer}.summary{background:#f7f9fb;border:1px solid #e8edf2;border-radius:11px;padding:11px 13px;margin:16px 0}.summary strong,.summary span,.summary b{display:block}.summary strong{font-size:13px}.summary span{font-size:11px;color:#128c8a;margin-top:3px}.summary b{font-size:10px;color:#718096;margin-top:3px}.date-scroller{display:grid;grid-auto-flow:column;grid-auto-columns:72px;gap:8px;overflow-x:auto;padding:2px 1px 10px}.day{border:1px solid #dfe6ed;background:#fff;border-radius:12px;padding:9px 5px;cursor:pointer;text-align:center}.day small,.day strong,.day span{display:block}.day small{font-size:10px;color:#718096}.day strong{font-size:20px;margin:3px 0}.day span{font-size:10px;color:#718096}.day.selected{background:#e9f7f5;border-color:#7bc9c4;color:#0d746f}.day.disabled{opacity:.4;cursor:not-allowed}.slot-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px}.slot-grid button{min-height:52px;border:1px solid #dfe6ed;background:#fff;border-radius:10px;cursor:pointer;font-weight:750;color:#334155}.slot-grid button.selected{background:#128c8a;border-color:#128c8a;color:#fff}.slot-grid button:disabled{background:#f1f3f5;color:#b2bac4;cursor:not-allowed;text-decoration:line-through}.slot-grid small{display:block;font-size:9px;font-weight:500;margin-top:2px}.loading,.empty{text-align:center;padding:25px;color:#718096;font-size:12px}.error{padding:10px 12px;background:#fbeaea;color:#a52e2e;border-radius:9px;font-size:12px;margin-top:14px}@media(max-width:500px){.slot-grid{grid-template-columns:repeat(3,1fr)}.card{padding:19px}}
</style>
