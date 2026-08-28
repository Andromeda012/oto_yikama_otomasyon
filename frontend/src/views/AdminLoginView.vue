<template>
  <main class="login-page">
    <form class="login-card" @submit.prevent="submit">
      <div class="brand-mark">CW</div>
      <p class="eyebrow">YÖNETİM PANELİ</p>
      <h1>Hoş geldiniz</h1>
      <p class="subtitle">İşletme yönetimine devam etmek için giriş yapın.</p>
      <div v-if="error" class="alert">{{ error }}</div>
      <label>Kullanıcı adı<input v-model.trim="username" autocomplete="username" required autofocus /></label>
      <label>Şifre<input v-model="password" type="password" autocomplete="current-password" required /></label>
      <button class="primary" :disabled="loading">{{ loading ? 'Giriş yapılıyor...' : 'Giriş Yap' }}</button>
      <RouterLink to="/" class="back">← Müşteri ekranına dön</RouterLink>
    </form>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { login } from '../services/auth';

const router = useRouter();
const route = useRoute();
const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

async function submit() {
  loading.value = true;
  error.value = '';
  try {
    await login(username.value, password.value);
    await router.replace(typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/admin/') ? route.query.redirect : '/admin/dashboard');
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page{min-height:100vh;display:grid;place-items:center;padding:24px;background:#f5f7fa}.login-card{width:min(420px,100%);background:#fff;border:1px solid #e3e8ef;border-radius:18px;padding:34px;box-shadow:0 18px 50px rgba(23,32,51,.07)}.brand-mark{width:48px;height:48px;border-radius:13px;background:#128c8a;color:#fff;display:grid;place-items:center;font-weight:850;margin-bottom:20px}.eyebrow{margin:0;color:#7b8797;text-transform:uppercase;font-size:10px;letter-spacing:.12em;font-weight:800}.login-card h1{margin:7px 0 5px;font-size:27px}.subtitle{margin:0 0 22px;color:#64748b;font-size:13px}.alert{margin-bottom:15px;padding:11px 12px;border-radius:9px;background:#fdecec;color:#bd3a3a;font-size:12px}label{display:block;margin-top:14px;color:#475569;font-size:12px;font-weight:700}input{display:block;width:100%;height:42px;margin-top:7px;border:1px solid #dce3ea;border-radius:9px;padding:0 12px;outline:none;color:#172033}input:focus{border-color:#7bc7c3;box-shadow:0 0 0 3px #edf7f6}.primary{width:100%;height:44px;margin-top:22px;border:0;border-radius:9px;background:#128c8a;color:#fff;font-weight:800;cursor:pointer}.primary:disabled{opacity:.65;cursor:wait}.back{display:block;text-align:center;margin-top:18px;color:#64748b;font-size:12px;text-decoration:none}.back:hover{color:#128c8a}
</style>
