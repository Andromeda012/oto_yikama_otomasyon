import { createRouter, createWebHistory } from "vue-router";
import PlaceholderView from "../views/PlaceholderView.vue";
import DashboardView from "../views/DashboardView.vue";
import AppointmentView from "../views/AppointmentView.vue";
import DefinitionsView from "../views/DefinitionsView.vue";
import VehicleTrackingView from "../views/VehicleTrackingView.vue";
import MarketView from "../views/MarketView.vue";
import AccountView from "../views/AccountView.vue";
import CompanyAccountView from "../views/CompanyAccountView.vue";
import SettingsView from "../views/SettingsView.vue";
import StatisticsView from "../views/StatisticsView.vue";

const routes = [
  { path: "/", name: "dashboard", component: DashboardView },
  { path: "/hesabim", name: "account", component: CompanyAccountView },
  { path: "/cari", name: "accounts", component: AccountView },
  { path: "/ayarlar/:subsection?", name: "settings", component: SettingsView },
  { path: "/tanimlar/:subsection?", name: "definitions", component: DefinitionsView },
  { path: "/yonetim/market", name: "market", component: MarketView },
  { path: "/yonetim/arac-takip", name: "operations", component: VehicleTrackingView },
  { path: "/yonetim/randevu", name: "appointments", component: AppointmentView },
  { path: "/istatistikler/:subsection?", name: "statistics", component: StatisticsView },
];

export default createRouter({ history: createWebHistory(), routes });
