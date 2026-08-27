<template>
<section class="settings-page">
  <header class="page-header">
    <div><p class="eyebrow">Sistem</p><h1>Ayarlar</h1><p>Randevu, çalışma saatleri ve iletişim kanallarının çalışma şeklini yönetin.</p></div>
    <button class="primary" :disabled="saving || loading" @click="save">{{ saving ? 'Kaydediliyor...' : 'Ayarları Kaydet' }}</button>
  </header>
  <div v-if="error" class="alert">{{ error }}</div><div v-if="success" class="success">{{ success }}</div>
  <div v-if="loading" class="loading">Ayarlar yükleniyor...</div>
  <form v-else class="sections" @submit.prevent="save">
    <section class="panel">
      <div class="panel-head"><h2>Genel ayarlar</h2><p>İşletmenin sistem içinde kullanacağı temel tercihler.</p></div>
      <div class="form-grid">
        <label>Saat dilimi<select v-model="form.timezone"><option value="Europe/Istanbul">Türkiye — Europe/Istanbul</option><option value="UTC">UTC</option></select></label>
        <label>Para birimi<select v-model="form.currency"><option value="TRY">TRY — Türk Lirası</option><option value="EUR">EUR — Euro</option><option value="USD">USD — Amerikan Doları</option></select></label>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head"><h2>Randevu ayarları</h2><p>Randevu ekranının davranışını belirleyin.</p></div>
      <div class="form-grid">
        <label>Randevu aralığı (dakika)<input v-model.number="form.appointment_slot_minutes" type="number" min="5" max="240" step="5" /></label>
        <label>En fazla kaç gün ileri?<input v-model.number="form.appointment_advance_days" type="number" min="0" max="365" /></label>
        <label class="switch-row"><input v-model="form.appointment_auto_job" type="checkbox" /><span><strong>Randevudan iş emri oluştur</strong><small>Randevu işleme alındığında araç takip kaydı oluşturulmasına izin ver.</small></span></label>
        <label class="switch-row"><input v-model="form.appointment_allow_past" type="checkbox" /><span><strong>Geçmiş saatlere randevu</strong><small>Normalde kapalı tutulması önerilir.</small></span></label>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head"><h2>Çalışma saatleri</h2><p>Randevu planlamasında kullanılacak işletme çalışma saatleri.</p></div>
      <div class="hours">
        <div v-for="day in days" :key="day.key" class="hour-row">
          <label class="day-toggle"><input v-model="form.business_hours[day.key].enabled" type="checkbox" /><strong>{{ day.label }}</strong></label>
          <div class="time-inputs"><input v-model="form.business_hours[day.key].open" type="time" :disabled="!form.business_hours[day.key].enabled" /><span>—</span><input v-model="form.business_hours[day.key].close" type="time" :disabled="!form.business_hours[day.key].enabled" /></div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head"><h2>Bildirim ve hatırlatma</h2><p>Randevu hatırlatmalarının temel ayarları. Gönderim sağlayıcısı bağlantısı ayrıca yapılandırılabilir.</p></div>
      <div class="form-grid">
        <label class="switch-row full"><input v-model="form.reminder_enabled" type="checkbox" /><span><strong>Randevu hatırlatmalarını etkinleştir</strong><small>Sağlayıcı bağlantısı kurulmadan gerçek mesaj gönderilmez.</small></span></label>
        <label>Hatırlatma zamanı (saat önce)<input v-model.number="form.reminder_hours_before" type="number" min="1" max="168" /></label>
      </div>
    </section>

    <section class="panel channels">
      <div class="panel-head"><h2>SMS</h2><p>SMS sağlayıcısının temel yapılandırması. API entegrasyonu sonraki aşamada bağlanabilir.</p></div>
      <div class="form-grid">
        <label class="switch-row full"><input v-model="form.sms_enabled" type="checkbox" /><span><strong>SMS bildirimlerini etkinleştir</strong><small>Etkinleştirmek yalnızca ayarı açar; sağlayıcı API'si olmadan mesaj gönderilmez.</small></span></label>
        <label>Sağlayıcı<select v-model="form.sms_provider"><option value="">Seçiniz</option><option value="netgsm">Netgsm</option><option value="iletimerkezi">İleti Merkezi</option><option value="other">Diğer</option></select></label>
        <label>Gönderici adı<input v-model="form.sms_sender" maxlength="50" placeholder="OTODYKAMA" /></label>
      </div>
    </section>

    <section class="panel channels">
      <div class="panel-head"><h2>WhatsApp</h2><p>WhatsApp Business sağlayıcısının temel yapılandırması.</p></div>
      <div class="form-grid">
        <label class="switch-row full"><input v-model="form.whatsapp_enabled" type="checkbox" /><span><strong>WhatsApp bildirimlerini etkinleştir</strong><small>API bağlantısı kurulmadan gerçek mesaj gönderilmez.</small></span></label>
        <label>Sağlayıcı<select v-model="form.whatsapp_provider"><option value="">Seçiniz</option><option value="meta">Meta WhatsApp Business</option><option value="twilio">Twilio</option><option value="other">Diğer</option></select></label>
        <label>İşletme WhatsApp numarası<input v-model="form.whatsapp_phone" type="tel" placeholder="905xxxxxxxxx" /></label>
      </div>
    </section>
  </form>
</section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { getSettings, updateSettings } from '../services/settings';
const days = [{key:'monday',label:'Pazartesi'},{key:'tuesday',label:'Salı'},{key:'wednesday',label:'Çarşamba'},{key:'thursday',label:'Perşembe'},{key:'friday',label:'Cuma'},{key:'saturday',label:'Cumartesi'},{key:'sunday',label:'Pazar'}];
const defaultHours = Object.fromEntries(days.map(d => [d.key,{enabled:true,open:'08:00',close:'19:00'}])); defaultHours.sunday.enabled=false; defaultHours.saturday.open='09:00'; defaultHours.saturday.close='18:00'; defaultHours.sunday.open='09:00'; defaultHours.sunday.close='17:00';
const form = reactive({ timezone:'Europe/Istanbul',currency:'TRY',appointment_slot_minutes:30,appointment_advance_days:30,appointment_allow_past:false,appointment_auto_job:true,reminder_enabled:false,reminder_hours_before:24,sms_enabled:false,sms_provider:'',sms_sender:'',whatsapp_enabled:false,whatsapp_provider:'',whatsapp_phone:'',business_hours:structuredClone(defaultHours) });
const loading=ref(true),saving=ref(false),error=ref(''),success=ref('');
async function load(){ loading.value=true; error.value=''; try{ const data=await getSettings(); Object.assign(form,data); form.business_hours=Object.assign(structuredClone(defaultHours),data.business_hours||{}); }catch(e){error.value=e.message||'Ayarlar alınamadı.'}finally{loading.value=false} }
async function save(){ error.value='';success.value=''; saving.value=true; try{ await updateSettings(form); success.value='Ayarlar başarıyla kaydedildi.'; }catch(e){error.value=e.message||'Ayarlar kaydedilemedi.'}finally{saving.value=false} }
onMounted(load);
</script>

<style scoped>
.settings-page{padding:30px;max-width:1100px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.primary{border:0;border-radius:10px;padding:11px 16px;background:#128c8a;color:#fff;font-weight:750;cursor:pointer}.primary:disabled{opacity:.5}.sections{display:grid;gap:16px}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:15px;overflow:hidden}.panel-head{padding:18px 20px;border-bottom:1px solid #edf0f4}.panel-head h2{margin:0;font-size:16px}.panel-head p{margin:5px 0 0;color:#64748b;font-size:12px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:20px}.form-grid label{display:grid;gap:7px;font-size:12px;font-weight:750;color:#334155}.form-grid .full{grid-column:1/-1}.form-grid input:not([type=checkbox]),.form-grid select{width:100%;border:1px solid #d8e0e8;border-radius:9px;padding:11px 12px;background:#fff;outline:none}.form-grid input:focus,.form-grid select:focus{border-color:#128c8a}.switch-row{display:flex!important;align-items:flex-start;gap:10px;padding:12px;border:1px solid #edf0f4;border-radius:10px}.switch-row input{margin-top:3px;accent-color:#128c8a}.switch-row strong,.switch-row small{display:block}.switch-row small{font-weight:400;color:#64748b;margin-top:4px;line-height:1.45}.hours{padding:8px 20px 18px}.hour-row{display:grid;grid-template-columns:220px 1fr;align-items:center;padding:10px 0;border-bottom:1px solid #f0f2f5}.day-toggle{display:flex;gap:10px;align-items:center;font-size:13px}.day-toggle input{accent-color:#128c8a}.time-inputs{display:flex;align-items:center;gap:10px;max-width:310px}.time-inputs input{border:1px solid #d8e0e8;border-radius:8px;padding:9px}.time-inputs span{color:#94a3b8}.alert,.success{margin-bottom:14px;padding:12px 14px;border-radius:9px;font-size:13px}.alert{background:#fbeaea;color:#a52e2e}.success{background:#eaf8f1;color:#187a59}.loading{text-align:center;background:#fff;border:1px solid #e3e8ef;border-radius:15px;padding:60px;color:#64748b}@media(max-width:700px){.settings-page{padding:18px}.page-header{align-items:flex-start;flex-direction:column}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.hour-row{grid-template-columns:1fr;gap:10px}.time-inputs{max-width:none}.time-inputs input{flex:1}}
</style>
