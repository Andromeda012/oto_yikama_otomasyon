<template>
  <main class="account-page">
    <header class="top"><RouterLink to="/" class="back">‹</RouterLink><div><strong>Hesabım</strong><small>Bilgilerinizi kaydedin</small></div><span></span></header>
    <div class="content">
      <section class="card intro"><p class="eyebrow">MÜŞTERİ HESABI</p><h1>Bilgilerinizi bir kez kaydedin</h1><p>Hesabım zorunlu değildir. Bilgilerinizi kaydettiğinizde randevu alırken tekrar yazmanız gerekmez; cari ve araç kaydınız işletme sistemine otomatik olarak oluşturulur.</p></section>
      <form class="card" @submit.prevent="save">
        <p class="eyebrow">KİŞİ BİLGİLERİ</p><div class="grid"><label>Ad *<input v-model="form.first_name" required autocomplete="given-name"></label><label>Soyad *<input v-model="form.last_name" required autocomplete="family-name"></label></div>
        <label>Telefon *<input v-model="form.phone" required type="tel" autocomplete="tel" placeholder="05xx xxx xx xx"></label>
        <label>E-posta <span class="optional">(opsiyonel)</span><input v-model="form.email" type="email" autocomplete="email"></label>
        <label>Not <span class="optional">(opsiyonel)</span><textarea v-model="form.notes" rows="3" placeholder="İletişim veya özel not..."/></label>
        <p class="eyebrow section">ARAÇ BİLGİLERİ</p><label>Plaka *<input v-model="form.plate" required @input="form.plate=form.plate.toUpperCase()" placeholder="34 ABC 123"></label>
        <div class="grid"><label>Marka<input v-model="form.brand" placeholder="Örn. BMW"></label><label>Model<input v-model="form.model" placeholder="Örn. 3 Serisi"></label></div>
        <div class="grid"><label>Yıl<input v-model.number="form.year" type="number" min="1950" max="2100"></label><label>Renk<input v-model="form.color" placeholder="Örn. Siyah"></label></div>
        <label>Araç notu <span class="optional">(opsiyonel)</span><textarea v-model="form.vehicle_notes" rows="3" placeholder="Araçla ilgili not..."/></label>
        <p v-if="error" class="error">{{error}}</p><p v-if="success" class="success">{{success}}</p>
        <button class="primary" :disabled="saving">{{saving?'Kaydediliyor…':'Bilgilerimi Kaydet'}}</button>
      </form>
      <section v-if="savedVehicle" class="card saved"><p class="eyebrow">KAYITLI ARAÇ</p><strong>{{savedVehicle.plate}}</strong><span>{{[savedVehicle.brand,savedVehicle.model,savedVehicle.year,savedVehicle.color].filter(Boolean).join(' · ') || 'Araç bilgileri kayıtlı.'}}</span></section>
    </div>
    <nav class="bottom"><RouterLink to="/"><span>⌂</span>Ana Sayfa</RouterLink><RouterLink to="/musteri/randevu-al"><span>＋</span>Randevu Al</RouterLink><RouterLink to="/musteri/randevu-takip"><span>◷</span>Takip</RouterLink><RouterLink to="/musteri/ayarlar"><span>⚙</span>Ayarlar</RouterLink></nav>
  </main>
</template>
<script setup>
import { onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { getCustomerProfile, saveCustomerProfile } from "../services/customer";
const form=reactive({first_name:"",last_name:"",phone:"",email:"",notes:"",plate:"",brand:"",model:"",year:null,color:"",vehicle_notes:""});
const saving=ref(false),error=ref(""),success=ref(""),savedVehicle=ref(null);
async function load(){try{const saved=JSON.parse(sessionStorage.getItem("customer_profile")||"null");if(saved?.phone){Object.assign(form,saved)}if(form.phone){const data=await getCustomerProfile(form.phone);if(data.account){Object.assign(form,data.account);const v=data.vehicles?.[0];if(v){Object.assign(form,{plate:v.plate,brand:v.brand,model:v.model,year:v.year,color:v.color,vehicle_notes:v.notes});savedVehicle.value=v}}}}catch{}}
async function save(){saving.value=true;error.value="";success.value="";try{const data=await saveCustomerProfile({...form});Object.assign(form,{...data.account,plate:data.vehicle.plate,brand:data.vehicle.brand,model:data.vehicle.model,year:data.vehicle.year,color:data.vehicle.color,vehicle_notes:data.vehicle.notes});savedVehicle.value=data.vehicle;sessionStorage.setItem("customer_profile",JSON.stringify({...form}));sessionStorage.setItem("customer_lookup",JSON.stringify({phone:form.phone,plate:form.plate}));success.value="Bilgileriniz kaydedildi. Randevu alırken otomatik kullanılacaktır."}catch(e){error.value=e.message}finally{saving.value=false}}
onMounted(load)
</script>
<style scoped>
.account-page{min-height:100vh;background:#f5f7fa;color:#172033;padding-bottom:85px}.top{height:68px;background:#fff;border-bottom:1px solid #e6eaf0;display:grid;grid-template-columns:44px 1fr 44px;align-items:center;padding:0 18px;position:sticky;top:0;z-index:10}.top strong,.top small{display:block}.top strong{font-size:15px}.top small{font-size:10px;color:#7b8797;margin-top:2px}.back{text-decoration:none;color:#334155;font-size:30px}.content{max-width:650px;margin:auto;padding:22px 18px;display:grid;gap:14px}.card{background:#fff;border:1px solid #e1e7ee;border-radius:18px;padding:22px;box-shadow:0 10px 30px rgba(23,32,51,.04)}.eyebrow{font-size:10px;letter-spacing:.11em;font-weight:850;color:#128c8a;margin:0 0 7px}.intro h1{font-size:24px;margin:0 0 8px}.intro p:last-child{font-size:12px;color:#718096;line-height:1.6;margin:0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.card label{display:grid;gap:6px;font-size:12px;font-weight:750;color:#334155;margin-top:13px}.optional{font-size:10px;color:#94a3b8;font-weight:500}.card input,.card textarea{width:100%;box-sizing:border-box;border:1px solid #d8e0e8;border-radius:10px;padding:12px;outline:none;background:#fff;font:inherit}.card textarea{resize:vertical}.section{margin-top:27px}.primary{width:100%;border:0;background:#128c8a;color:#fff;border-radius:11px;padding:13px 15px;font-weight:800;cursor:pointer;margin-top:18px}.primary:disabled{opacity:.5}.error,.success{padding:10px 12px;border-radius:9px;font-size:12px;margin:14px 0 0}.error{background:#fbeaea;color:#a52e2e}.success{background:#e9f7f5;color:#0d746f}.saved strong,.saved span{display:block}.saved strong{font-size:17px}.saved span{font-size:11px;color:#718096;margin-top:4px}.bottom{position:fixed;bottom:0;left:0;right:0;height:70px;background:rgba(255,255,255,.97);border-top:1px solid #e5e9ef;display:flex;justify-content:center;gap:38px;z-index:20}.bottom a{min-width:55px;text-decoration:none;color:#718096;font-size:10px;font-weight:700;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px}.bottom span{font-size:17px}.bottom .router-link-active{color:#128c8a}@media(max-width:500px){.grid{grid-template-columns:1fr}.card{padding:18px}.bottom{gap:18px}}
</style>
