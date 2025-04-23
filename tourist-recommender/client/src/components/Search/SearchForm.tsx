// client/src/components/Search/SearchForm.tsx
import React, { useState } from "react";
import { getRecommendations } from "../../services/api";

const SearchForm: React.FC = () => {
  const [interests, setInterests] = useState<string[]>([]);
  const [duration, setDuration] = useState<number>(4); // Horas
  const [budget, setBudget] = useState<"low" | "medium" | "high">("medium");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const recommendations = await getRecommendations({
      interests,
      duration,
      budget,
    });
    console.log(recommendations); // Aquí podrías guardar los resultados en un estado global (Redux/Context)
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Intereses:</label>
        <select
          multiple
          onChange={(e) =>
            setInterests(
              Array.from(e.target.selectedOptions, (opt) => opt.value)
            )
          }
        >
          <option value="cultural">Cultural</option>
          <option value="nature">Naturaleza</option>
          <option value="food">Gastronomía</option>
        </select>
      </div>
      <div>
        <label>Duración (horas):</label>
        <input
          type="number"
          value={duration}
          onChange={(e) => setDuration(Number(e.target.value))}
        />
      </div>
      <div>
        <label>Presupuesto:</label>
        <select
          value={budget}
          onChange={(e) => setBudget(e.target.value as any)}
        >
          <option value="low">Bajo</option>
          <option value="medium">Medio</option>
          <option value="high">Alto</option>
        </select>
      </div>
      <button type="submit">Buscar Recomendaciones</button>
    </form>
  );
};

export default SearchForm;
