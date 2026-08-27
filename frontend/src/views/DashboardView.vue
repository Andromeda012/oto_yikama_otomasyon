<template>
  <section class="dashboard">
    <div class="welcome"><h1>Hoş geldiniz 👋</h1><p>Bugünkü işletme durumunu hızlıca gözden geçirin.</p></div>
    <div class="cards">
      <div class="stat-card"><div class="stat-label">BUGÜNKÜ RANDEVULAR</div><div class="stat-value">12</div><div class="stat-note">3 randevu bekliyor</div></div>
      <div class="stat-card"><div class="stat-label">İŞLEMDEKİ ARAÇLAR</div><div class="stat-value">5</div><div class="stat-note">2 araç kontrol aşamasında</div></div>
      <div class="stat-card"><div class="stat-label">BUGÜNKÜ CİRO</div><div class="stat-value">8.450 TL</div><div class="stat-note">Demo verisi</div></div>
      <div class="stat-card"><div class="stat-label">KRİTİK STOK</div><div class="stat-value">2</div><div class="stat-note">Kontrol edilmesi gereken ürün</div></div>
    </div>
    <div class="dashboard-grid">
      <div class="panel"><h2>Bugünkü Randevular</h2><div class="quick-list"><div class="quick-row"><div><strong>09:30 · BMW 320 · 34 ABC 123</strong><span> Ahmet · Detaylı Temizlik</span></div><span>Planlandı</span></div><div class="quick-row"><div><strong>10:00 · Audi A4 · 16 XYZ 456</strong><span> Mehmet · İç + Dış</span></div><span>Geldi</span></div><div class="quick-row"><div><strong>10:30 · Mercedes · 06 DEF 789</strong><span> Ayşe · Pasta / Cila</span></div><span>Planlandı</span></div></div></div>
      <div class="panel"><h2>Hızlı İşlemler</h2><div class="quick-actions"><RouterLink class="quick-action" to="/yonetim/randevu">+ Yeni Randevu</RouterLink><RouterLink class="quick-action" to="/yonetim/arac-takip">Araç Takibi</RouterLink><RouterLink class="quick-action" to="/yonetim/market">Satış Ekranı</RouterLink><RouterLink class="quick-action" to="/tanimlar">Tanımlar</RouterLink></div></div>
    </div>
  </section>
</template>
<script setup>
import { RouterLink } from 'vue-router';
</script>
