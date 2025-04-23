import { Coordinates, TimeRange, DayOfWeek } from "./Basic";

export interface IAttraction {
  id: string;
  name: string;
  description: string;
  location: Coordinates;
  categories: TourismCategory[];
  openingHours: {
    weekdays: TimeRange;
    weekends?: TimeRange;
    exceptionalDays?: {
      date: string; // YYYY-MM-DD
      hours: TimeRange | "closed";
    }[];
    daysOpen: DayOfWeek[];
  };
  price: {
    adult: number;
    child?: number;
    senior?: number;
    currency: "EUR" | "USD"; // Ajustar según necesidad
  };
  averageVisitDuration: number; // En minutos
  popularity: number; // Escala 1-10
  images?: string[]; // URLs de imágenes
  reviews?: IReview[];
}

export type TourismCategory =
  | "museum"
  | "monument"
  | "park"
  | "gallery"
  | "religious"
  | "shopping"
  | "gastronomy"
  | "adventure"
  | "family"
  | string; // Para categorías personalizadas

export interface IReview {
  userId: string;
  rating: number; // 1-5
  comment: string;
  date: string; // ISO format
}
