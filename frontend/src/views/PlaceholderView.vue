<template>
  <section class="placeholder-page">
    <div class="placeholder-icon">◆</div>
    <p class="eyebrow">Modül</p>
    <h1>{{ title }}</h1>
    <p>Bu bölümün işlevsel özellikleri sonraki geliştirme aşamalarında eklenecek.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
const route = useRoute();
const titles = { '/hesabim':'Hesabım', '/ayarlar':'Ayarlar', '/tanimlar':'Tanımlar', '/yonetim/market':'Market Satış', '/yonetim/arac-takip':'Araç Takibi', '/istatistikler':'İstatistikler' };
const title = computed(() => titles[route.path] || 'Bu sayfa');
</script>

<style scoped>
.placeholder-page{min-height:calc(100vh - 72px);display:grid;place-content:center;text-align:center;padding:30px;color:#64748b}.placeholder-icon{width:54px;height:54px;border-radius:15px;background:#e7f6f4;color:#128c8a;display:grid;place-items:center;margin:0 auto 18px}.eyebrow{margin:0;text-transform:uppercase;letter-spacing:.1em;font-size:11px;font-weight:800}.placeholder-page h1{color:#172033;margin:7px 0;font-size:28px}.placeholder-page p:last-child{max-width:500px;margin:0 auto;line-height:1.6}
</style>
