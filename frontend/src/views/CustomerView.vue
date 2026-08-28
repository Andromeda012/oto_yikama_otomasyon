<template>
  <main class="customer-app">
    <header class="customer-header">
      <div class="brand">
        <div class="logo">{{ initials }}</div>
        <div><strong>{{ companyName }}</strong><span>Online İşlemler</span></div>
      </div>
      <RouterLink to="/admin/login" class="admin-link">Yönetim</RouterLink>
    </header>

    <section class="hero">
      <p class="eyebrow">HOŞ GELDİNİZ</p>
      <h1>Aracınız için işlemlerinizi kolayca yönetin.</h1>
      <p>Randevunuzu oluşturun veya mevcut randevunuzu takip edin.</p>
    </section>

    <section class="main-actions">
      <RouterLink to="/musteri/randevu-al" class="action-card primary-card">
        <span class="action-icon">＋</span><div><strong>Randevu Al</strong><small>Size uygun gün ve saati seçin.</small></div><b>›</b>
      </RouterLink>
      <RouterLink to="/musteri/randevu-takip" class="action-card">
        <span class="action-icon">◷</span><div><strong>Randevu Takip</strong><small>Randevunuzu görüntüleyin veya değiştirin.</small></div><b>›</b>
      </RouterLink>
    </section>

    <section class="info-card">
      <span>📍</span><div><strong>Hızlı ve kolay</strong><small>Telefonla iletişime geçmeden online randevu oluşturabilirsiniz.</small></div>
    </section>

    <nav class="bottom-nav">
      <RouterLink to="/musteri/hesabim"><span>◉</span>Hesabım</RouterLink>
      <RouterLink to="/musteri/ayarlar"><span>⚙</span>Ayarlar</RouterLink>
    </nav>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { getCompanyPublic } from "../services/customer";

const companyName = ref("Oto Yıkama");
const initials = computed(() => companyName.value.split(/\s+/).filter(Boolean).slice(0, 2).map(x => x[0]).join("").toUpperCase() || "OY");
onMounted(async () => { try { const data = await getCompanyPublic(); companyName.value = data.company_name || companyName.value; } catch {} });
</script>

<style scoped>
.customer-app{min-height:100vh;background:#f5f7fa;color:#172033;padding-bottom:88px}.customer-header{max-width:760px;margin:auto;padding:20px 20px 10px;display:flex;justify-content:space-between;align-items:center}.brand{display:flex;align-items:center;gap:11px}.logo{width:44px;height:44px;border-radius:13px;background:#128c8a;color:#fff;display:grid;place-items:center;font-weight:850}.brand strong,.brand span{display:block}.brand strong{font-size:16px}.brand span{font-size:11px;color:#7b8797;margin-top:2px}.admin-link{font-size:11px;color:#64748b;text-decoration:none}.hero{max-width:760px;margin:20px auto 24px;padding:0 20px}.eyebrow{font-size:10px;letter-spacing:.12em;font-weight:850;color:#128c8a;margin:0 0 8px}.hero h1{font-size:30px;line-height:1.16;margin:0 0 9px;max-width:560px}.hero p:last-child{margin:0;color:#64748b;line-height:1.55}.main-actions{max-width:760px;margin:auto;padding:0 20px;display:grid;gap:12px}.action-card{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid #e1e7ee;border-radius:17px;padding:18px;text-decoration:none;color:#172033;box-shadow:0 7px 22px rgba(23,32,51,.04)}.primary-card{border-color:#b9dfdc}.action-icon{width:43px;height:43px;border-radius:12px;background:#e9f7f5;color:#128c8a;display:grid;place-items:center;font-size:22px;flex:none}.action-card div{flex:1}.action-card strong,.action-card small{display:block}.action-card strong{font-size:16px}.action-card small{font-size:12px;color:#718096;margin-top:4px}.action-card b{font-size:24px;color:#9aa6b5;font-weight:400}.info-card{max-width:720px;margin:18px auto 0;padding:14px 20px;display:flex;gap:10px;color:#64748b}.info-card strong,.info-card small{display:block}.info-card strong{font-size:12px;color:#475569}.info-card small{font-size:11px;margin-top:3px;line-height:1.4}.bottom-nav{position:fixed;bottom:0;left:0;right:0;height:70px;background:rgba(255,255,255,.97);border-top:1px solid #e5e9ef;display:flex;justify-content:center;gap:90px;z-index:20}.bottom-nav a{min-width:70px;text-decoration:none;color:#718096;font-size:11px;font-weight:700;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}.bottom-nav span{font-size:18px}.bottom-nav .router-link-active{color:#128c8a}@media(min-width:700px){.customer-app{background:#f5f7fa}.main-actions{grid-template-columns:1fr 1fr}.hero{margin-top:45px}.bottom-nav{position:static;max-width:760px;margin:28px auto 0;border:0;background:transparent;justify-content:flex-start;gap:24px}.bottom-nav a{flex-direction:row;min-width:auto}.bottom-nav span{font-size:15px}}
</style>
