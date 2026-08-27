<template>
  <section class="account-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">İşletme</p>
        <h1>Hesabım</h1>
        <p>İşletmenizin kimlik ve iletişim bilgilerini yönetin.</p>
      </div>
      <button class="primary" :disabled="saving || loading" @click="save">{{ saving ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet' }}</button>
    </header>

    <div v-if="error" class="alert">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div v-if="loading" class="loading">Bilgiler yükleniyor...</div>
    <form v-else class="grid" @submit.prevent="save">
      <section class="panel main-panel">
        <div class="panel-head"><div><h2>İşletme bilgileri</h2><p>Fatura ve işletme tanımlamalarında kullanılabilecek temel bilgiler.</p></div></div>
        <div class="form-grid">
          <label class="full">İşletme adı *<input v-model="form.company_name" required placeholder="Örn. Eren Oto Yıkama" /></label>
          <label class="full">Ticari / resmi unvan<input v-model="form.legal_name" placeholder="Resmi şirket unvanı" /></label>
          <label>Vergi numarası<input v-model="form.tax_number" placeholder="Vergi numarası" /></label>
          <label>Vergi dairesi<input v-model="form.tax_office" placeholder="Vergi dairesi" /></label>
        </div>
      </section>

      <section class="panel contact-panel">
        <div class="panel-head"><div><h2>İletişim bilgileri</h2><p>Müşteri iletişimi ve işletme iletişim kanalları.</p></div></div>
        <div class="form-grid">
          <label>Telefon<input v-model="form.phone" type="tel" placeholder="05xx xxx xx xx" /></label>
          <label>E-posta<input v-model="form.email" type="email" placeholder="info@isletme.com" /></label>
          <label class="full">Web sitesi<input v-model="form.website" type="url" placeholder="https://..." /></label>
        </div>
      </section>

      <section class="panel address-panel">
        <div class="panel-head"><div><h2>Adres</h2><p>İşletmenin fiziksel adresi.</p></div></div>
        <div class="form-grid">
          <label class="full">Adres<textarea v-model="form.address" rows="4" placeholder="Mahalle, cadde, sokak, bina..." /></label>
          <label>İl<input v-model="form.city" placeholder="İl" /></label>
          <label>İlçe<input v-model="form.district" placeholder="İlçe" /></label>
        </div>
      </section>

      <aside class="panel info-panel">
        <div class="info-icon">✓</div>
        <h2>Hesap bilgileri</h2>
        <p>Buradaki bilgiler işletmenin genel profilini tanımlar.</p>
        <ul><li>Randevu ve satış ekranlarında işletme bilgileri için kullanılabilir.</li><li>SMS ve WhatsApp ayarları daha sonra <strong>Ayarlar</strong> bölümünden yönetilecek.</li><li>Vergi ve resmi bilgiler finans modüllerinden bağımsız tutulur.</li></ul>
      </aside>
    </form>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { getCompanyProfile, updateCompanyProfile } from '../services/company';

const form = reactive({ company_name:'', legal_name:'', tax_number:'', tax_office:'', phone:'', email:'', website:'', address:'', city:'', district:'' });
const loading = ref(true), saving = ref(false), error = ref(''), success = ref('');
async function load() {
  loading.value = true; error.value = '';
  try { Object.assign(form, await getCompanyProfile()); }
  catch (e) { error.value = e.message || 'İşletme bilgileri alınamadı.'; }
  finally { loading.value = false; }
}
async function save() {
  error.value = ''; success.value = '';
  if (!form.company_name.trim()) { error.value = 'İşletme adı zorunludur.'; return; }
  saving.value = true;
  try { Object.assign(form, await updateCompanyProfile(form)); success.value = 'İşletme bilgileri başarıyla kaydedildi.'; }
  catch (e) { error.value = e.message || 'Bilgiler kaydedilemedi.'; }
  finally { saving.value = false; }
}
onMounted(load);
</script>

<style scoped>
.account-page{padding:30px;max-width:1200px;margin:auto}.page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.page-header h1{margin:4px 0;font-size:30px}.page-header p:last-child{margin:0;color:#64748b}.eyebrow{margin:0;color:#64748b;text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.08em}.primary{border:0;border-radius:10px;padding:11px 16px;background:#128c8a;color:#fff;font-weight:750;cursor:pointer}.primary:disabled{opacity:.5;cursor:not-allowed}.grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(300px,.65fr);gap:16px}.panel{background:#fff;border:1px solid #e3e8ef;border-radius:15px;overflow:hidden}.main-panel{grid-column:1}.contact-panel{grid-column:1}.address-panel{grid-column:1}.info-panel{grid-column:2;grid-row:1 / span 3;padding:24px;align-self:start}.panel-head{padding:18px 20px;border-bottom:1px solid #edf0f4}.panel-head h2{margin:0;font-size:16px}.panel-head p{margin:5px 0 0;color:#64748b;font-size:12px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:20px}.form-grid label{display:grid;gap:7px;font-size:12px;font-weight:750;color:#334155}.form-grid .full{grid-column:1/-1}.form-grid input,.form-grid textarea{width:100%;border:1px solid #d8e0e8;border-radius:9px;padding:11px 12px;background:#fff;outline:none;resize:vertical}.form-grid input:focus,.form-grid textarea:focus{border-color:#128c8a;box-shadow:0 0 0 3px rgba(18,140,138,.09)}.info-icon{width:42px;height:42px;border-radius:12px;background:#e8f7f5;color:#128c8a;display:grid;place-items:center;font-weight:900;font-size:20px}.info-panel h2{margin:16px 0 6px;font-size:17px}.info-panel p,.info-panel li{font-size:12px;line-height:1.6;color:#64748b}.info-panel ul{padding-left:18px}.loading{text-align:center;background:#fff;border:1px solid #e3e8ef;border-radius:15px;padding:60px;color:#64748b}.alert,.success{margin-bottom:14px;padding:12px 14px;border-radius:9px;font-size:13px}.alert{background:#fbeaea;color:#a52e2e}.success{background:#eaf8f1;color:#187a59}@media(max-width:800px){.grid{grid-template-columns:1fr}.main-panel,.contact-panel,.address-panel,.info-panel{grid-column:1;grid-row:auto}.page-header{align-items:flex-start;flex-direction:column}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.account-page{padding:18px}}
</style>
