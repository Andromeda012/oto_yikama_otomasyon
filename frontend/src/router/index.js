import { createRouter, createWebHistory } from "vue-router";
import PlaceholderView from "../views/PlaceholderView.vue";
import DashboardView from "../views/DashboardView.vue";
import AppointmentView from "../views/AppointmentView.vue";
import DefinitionsView from "../views/DefinitionsView.vue";

const routes = [
  { path: "/", name: "dashboard", component: DashboardView },
  { path: "/hesabim", name: "account", component: PlaceholderView },
  { path: "/ayarlar/:subsection?", name: "settings", component: PlaceholderView },
  { path: "/tanimlar/:subsection?", name: "definitions", component: DefinitionsView },
  { path: "/yonetim/market", name: "market", component: PlaceholderView },
  { path: "/yonetim/arac-takip", name: "operations", component: PlaceholderView },
  { path: "/yonetim/randevu", name: "appointments", component: AppointmentView },
  { path: "/istatistikler/:subsection?", name: "statistics", component: PlaceholderView },
];

export default createRouter({ history: createWebHistory(), routes });
