<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">CW</div>
        <div><strong>Car Wash</strong><span>Automation</span></div>
      </div>

      <nav class="nav">
        <RouterLink to="/" class="nav-item"><span>⌂</span> Dashboard</RouterLink>

        <div class="nav-group">YÖNETİM</div>
        <RouterLink to="/yonetim/market" class="nav-item"><span>▣</span> Market Satış</RouterLink>
        <RouterLink to="/yonetim/arac-takip" class="nav-item"><span>🚗</span> Araç Takibi</RouterLink>
        <RouterLink to="/yonetim/randevu" class="nav-item"><span>◷</span> Randevu Yönetimi</RouterLink>

        <div class="nav-group">TANIMLAR</div>
        <RouterLink to="/tanimlar/urunler" class="nav-item"><span>▥</span> Ürün / Stok</RouterLink>
        <RouterLink to="/tanimlar/hizmetler" class="nav-item"><span>◇</span> Hizmetler</RouterLink>
        <RouterLink to="/tanimlar/personel" class="nav-item"><span>♙</span> Personel</RouterLink>
        <RouterLink to="/tanimlar/araclar" class="nav-item"><span>🚘</span> Araçlar</RouterLink>
        <RouterLink to="/cari" class="nav-item"><span>₺</span> Cari</RouterLink>

        <div class="nav-group">RAPORLAMA</div>
        <RouterLink to="/istatistikler" class="nav-item"><span>▤</span> İstatistikler</RouterLink>

        <div class="nav-spacer"></div>
        <RouterLink to="/hesabim" class="nav-item"><span>◉</span> Hesabım</RouterLink>
        <RouterLink to="/ayarlar" class="nav-item"><span>⚙</span> Ayarlar</RouterLink>
      </nav>

      <div class="sidebar-footer">Car Wash Automation<br><small>Yönetim Sistemi</small></div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <div>
          <div class="topbar-title">Oto Yıkama Yönetim Sistemi</div>
          <div class="topbar-subtitle">İşletmenizi tek ekrandan yönetin.</div>
        </div>
        <div class="profile">Yönetici <span>⌄</span></div>
      </header>
      <div class="page-content">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172033;background:#f5f7fa;font-synthesis:none;text-rendering:optimizeLegibility}
*{box-sizing:border-box}body{margin:0;min-width:320px;background:#f5f7fa}button,input,select,textarea{font:inherit}
.app-shell{min-height:100vh;display:flex}.sidebar{position:fixed;inset:0 auto 0 0;width:250px;background:#111827;color:#dbe3ec;display:flex;flex-direction:column;padding:22px 14px;z-index:10}.brand{display:flex;align-items:center;gap:11px;padding:4px 10px 28px;color:#fff}.brand-mark{width:38px;height:38px;border-radius:10px;background:#128c8a;display:grid;place-items:center;font-weight:800;font-size:13px}.brand strong,.brand span{display:block}.brand strong{font-size:15px}.brand span{font-size:11px;color:#94a3b8;margin-top:2px}.nav{display:flex;flex-direction:column;gap:4px;flex:1;min-height:0;overflow:auto;padding-bottom:4px}.nav-spacer{flex:1;min-height:24px}.nav-item{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:9px;color:#b9c3d0;text-decoration:none;font-size:14px;font-weight:600}.nav-item span{width:20px;text-align:center;opacity:.9}.nav-item:hover{background:#1f2937;color:#fff}.nav-item.router-link-active{background:#128c8a;color:#fff}.nav-group{font-size:10px;letter-spacing:.12em;color:#667085;font-weight:800;padding:18px 12px 6px}.sidebar-footer{margin-top:auto;padding:14px 10px;color:#64748b;font-size:11px;border-top:1px solid #263142;line-height:1.5}.sidebar-footer small{color:#475569}.main-content{margin-left:250px;width:calc(100% - 250px);min-height:100vh}.topbar{height:72px;background:#fff;border-bottom:1px solid #e6eaf0;display:flex;align-items:center;justify-content:space-between;padding:0 30px}.topbar-title{font-weight:750;font-size:15px}.topbar-subtitle{font-size:12px;color:#7b8797;margin-top:2px}.profile{font-size:13px;font-weight:650;color:#334155}.profile span{margin-left:7px;color:#94a3b8}.page-content{min-height:calc(100vh - 72px)}
.dashboard{padding:30px;max-width:1450px}.welcome h1{margin:0;font-size:28px}.welcome p{margin:6px 0 25px;color:#64748b}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.stat-card{background:#fff;border:1px solid #e4e9ef;border-radius:14px;padding:20px}.stat-label{font-size:12px;color:#64748b;font-weight:700}.stat-value{font-size:27px;font-weight:800;margin-top:8px}.stat-note{font-size:11px;color:#94a3b8;margin-top:5px}.dashboard-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:16px;margin-top:18px}.panel{background:#fff;border:1px solid #e4e9ef;border-radius:14px;padding:20px}.panel h2{font-size:16px;margin:0 0 16px}.quick-list{display:grid;gap:10px}.quick-row{display:flex;align-items:center;justify-content:space-between;padding:12px;border:1px solid #edf0f4;border-radius:10px}.quick-row strong{font-size:13px}.quick-row span{font-size:12px;color:#64748b}.quick-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}.quick-action{padding:14px;border:1px solid #e4e9ef;border-radius:10px;text-decoration:none;color:#1f2937;font-size:13px;font-weight:700}.quick-action:hover{border-color:#128c8a;color:#128c8a}
@media(max-width:900px){.sidebar{width:210px}.main-content{margin-left:210px;width:calc(100% - 210px)}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.dashboard-grid{grid-template-columns:1fr}}@media(max-width:650px){.sidebar{position:static;width:100%;min-height:auto}.app-shell{display:block}.main-content{margin-left:0;width:100%}.nav{display:grid;grid-template-columns:1fr 1fr}.nav-group{grid-column:1/-1}.nav-spacer{display:none}.sidebar-footer{display:none}.topbar{padding:0 16px}.dashboard-page{padding:18px}.cards{grid-template-columns:1fr 1fr}}
</style>
