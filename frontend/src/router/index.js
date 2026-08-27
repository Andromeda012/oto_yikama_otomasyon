import { createRouter, createWebHistory } from "vue-router";
import PlaceholderView from "../views/PlaceholderView.vue";
import AppointmentView from "../views/AppointmentView.vue";

const routes = [
  { path: "/", name: "dashboard", component: PlaceholderView },
  { path: "/hesabim", name: "account", component: PlaceholderView },
  { path: "/ayarlar/:subsection?", name: "settings", component: PlaceholderView },
  { path: "/tanimlar/:subsection?", name: "definitions", component: PlaceholderView },
  { path: "/yonetim/market", name: "market", component: PlaceholderView },
  { path: "/yonetim/arac-takip", name: "operations", component: PlaceholderView },
  { path: "/yonetim/randevu", name: "appointments", component: AppointmentView },
  { path: "/istatistikler/:subsection?", name: "statistics", component: PlaceholderView },
];

export default createRouter({ history: createWebHistory(), routes });
