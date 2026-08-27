import { createRouter, createWebHistory } from "vue-router";
import PlaceholderView from "../views/PlaceholderView.vue";
import DashboardView from "../views/DashboardView.vue";
import AppointmentView from "../views/AppointmentView.vue";
import DefinitionsView from "../views/DefinitionsView.vue";
import VehicleTrackingView from "../views/VehicleTrackingView.vue";
import MarketView from "../views/MarketView.vue";

const routes = [
  { path: "/", name: "dashboard", component: DashboardView },
  { path: "/hesabim", name: "account", component: PlaceholderView },
  { path: "/ayarlar/:subsection?", name: "settings", component: PlaceholderView },
  { path: "/tanimlar/:subsection?", name: "definitions", component: DefinitionsView },
  { path: "/yonetim/market", name: "market", component: MarketView },
  { path: "/yonetim/arac-takip", name: "operations", component: VehicleTrackingView },
  { path: "/yonetim/randevu", name: "appointments", component: AppointmentView },
  { path: "/istatistikler/:subsection?", name: "statistics", component: PlaceholderView },
];

export default createRouter({ history: createWebHistory(), routes });
