const { useEffect, useMemo, useState } = React;
const API_BASE_URL = ""; // e.g. "https://nox-web.onrender.com" for GitHub Pages frontend
const ANDROID_APP_URL = "downloads/NOX-android-latest.apk";
const ANDROID_APP_AVAILABLE = true;

async function api(path, options = {}) {
  const normalizedBase = API_BASE_URL.trim().replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = normalizedBase ? `${normalizedBase}${normalizedPath}` : normalizedPath;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

function Field({ label, children }) {
  return (
    <div>
      <label>{label}</label>
      {children}
    </div>
  );
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [workouts, setWorkouts] = useState([]);
  const [meals, setMeals] = useState([]);
  const [plan, setPlan] = useState("");
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [goalForm, setGoalForm] = useState({ goal: "maintenance", daily_calorie_target: "" });
  const [workoutForm, setWorkoutForm] = useState({
    date: "",
    exercise: "",
    sets: "3",
    reps: "8",
    weight: "",
    duration_min: "45",
    rpe: "8",
    notes: "",
  });
  const [mealForm, setMealForm] = useState({ date: "", meal_name: "lunch", description: "" });
  const [recipeFilter, setRecipeFilter] = useState({ goal: "", max_calories: "", meal_type: "" });

  const athleteCards = useMemo(
    () => [
      {
        name: "Usain Bolt",
        role: "Velocity Architecture",
        image: "assets/athletes/usain-bolt.jpg",
      },
      {
        name: "Chris Bumstead",
        role: "Classic Physique Discipline",
        image: "assets/athletes/chris-bumstead.jpg",
      },
      {
        name: "Michael Phelps",
        role: "Volume Endurance Blueprint",
        image: "assets/athletes/michael-phelps.jpg",
      },
    ],
    []
  );

  async function refreshAll() {
    setLoading(true);
    setError("");
    try {
      const [dash, ws, ms, ap, rc] = await Promise.all([
        api("/api/dashboard"),
        api("/api/workouts?days=30"),
        api("/api/meals"),
        api("/api/adaptive-plan"),
        api("/api/recipes"),
      ]);
      setDashboard(dash);
      setGoalForm((f) => ({
        ...f,
        goal: dash.profile.goal,
        daily_calorie_target: String(dash.profile.daily_calorie_target),
      }));
      setWorkouts(ws.workouts || []);
      setMeals(ms.meals || []);
      setPlan(ap.plan || "");
      setRecipes(rc.recipes || []);
    } catch (err) {
      setError(err.message || "Failed to load data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshAll();
  }, []);

  async function submitGoal(e) {
    e.preventDefault();
    try {
      await api("/api/profile", {
        method: "POST",
        body: JSON.stringify({
          goal: goalForm.goal,
          daily_calorie_target: goalForm.daily_calorie_target ? Number(goalForm.daily_calorie_target) : null,
        }),
      });
      await refreshAll();
    } catch (err) {
      setError(err.message || "Goal update failed.");
    }
  }

  async function submitWorkout(e) {
    e.preventDefault();
    try {
      await api("/api/workouts", {
        method: "POST",
        body: JSON.stringify({
          ...workoutForm,
          sets: Number(workoutForm.sets),
          reps: Number(workoutForm.reps),
          weight: Number(workoutForm.weight || 0),
          duration_min: Number(workoutForm.duration_min || 0),
          rpe: Number(workoutForm.rpe || 7),
        }),
      });
      setWorkoutForm((f) => ({ ...f, exercise: "", weight: "", notes: "" }));
      await refreshAll();
    } catch (err) {
      setError(err.message || "Workout log failed.");
    }
  }

  async function submitMeal(e) {
    e.preventDefault();
    try {
      await api("/api/meals", {
        method: "POST",
        body: JSON.stringify(mealForm),
      });
      setMealForm((f) => ({ ...f, description: "" }));
      await refreshAll();
    } catch (err) {
      setError(err.message || "Meal log failed.");
    }
  }

  async function findRecipes(e) {
    e.preventDefault();
    try {
      const q = new URLSearchParams();
      if (recipeFilter.goal) q.set("goal", recipeFilter.goal);
      if (recipeFilter.meal_type) q.set("meal_type", recipeFilter.meal_type);
      if (recipeFilter.max_calories) q.set("max_calories", recipeFilter.max_calories);
      const data = await api(`/api/recipes?${q.toString()}`);
      setRecipes(data.recipes || []);
    } catch (err) {
      setError(err.message || "Recipe lookup failed.");
    }
  }

  const delta = dashboard ? dashboard.calories_today - dashboard.profile.daily_calorie_target : 0;
  const todayDate = new Date().toISOString().slice(0, 10);

  function jumpTo(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <>
      <div className="scanlines" />
      <div className="noise" />

      <main className="app">
        <header className="topbar">
          <div className="brand">NOX</div>
          <div className="topmeta">Train smart, fuel ruthless</div>
        </header>

        <section className="hero">
          <div className="hero-grid">
            <div className="hero-copy">
              <span className="kicker">adaptive performance tracker</span>
              <h1 className="glitch" data-text="NOX">
                NOX
              </h1>
              <h1 className="glitch hero-tagline" data-text="TRAIN SMART, FUEL RUTHLESS">
                TRAIN SMART, FUEL RUTHLESS
              </h1>
              <p>A center for your body metrics. Track training load, push adaptive routines, and tune them.</p>
              <div className="meta-row">
                <span className="meta-chip">Goal: {dashboard?.profile.goal || "..."}</span>
                <span className="meta-chip">Streak: {dashboard ? `${dashboard.workout_streak} day(s)` : "..."}</span>
                <span className="meta-chip">Target: {dashboard?.profile.daily_calorie_target || "..."} kcal</span>
              </div>
            </div>

            <div className="hero-right">
              {athleteCards.map((ath) => (
                <article key={ath.name} className="athlete-block">
                  <img
                    src={ath.image}
                    alt={ath.name}
                    onError={(e) => {
                      if (!e.currentTarget.src.includes("assets/athletes/placeholder.svg")) {
                        e.currentTarget.src = "assets/athletes/placeholder.svg";
                      }
                    }}
                  />
                  <div className="athlete-label">
                    {ath.name} | {ath.role}
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="marquee">
          <div className="marquee-track">
            {"FITNESS TELEMETRY // NUTRITION ENGINE // ADAPTIVE LOADING // RECIPE INTELLIGENCE // ".repeat(8)}
          </div>
        </section>

        <section className="quick-actions card">
          <h3>What do you want to do?</h3>
          <div className="quick-actions-grid">
            <button type="button" className="ghost-btn" onClick={() => jumpTo("goal-section")}>Set Goal</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("workout-section")}>Log Workout</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("meal-section")}>Log Meal</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("plan-section")}>View Adaptive Plan</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("history-section")}>See Workout History</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("recipe-section")}>Get Recipes</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("android-section")}>Get Android App</button>
            <button type="button" className="ghost-btn" onClick={refreshAll}>Refresh Data</button>
            <button type="button" className="ghost-btn" onClick={() => jumpTo("top")}>Back To Top</button>
          </div>
        </section>

        <section className="layout">
          <article className="card kpi" id="top">
            <h3>Calories Today</h3>
            <strong>{dashboard ? Math.round(dashboard.calories_today) : "..."}</strong>
            <span>Daily energy intake logged ({todayDate})</span>
          </article>

          <article className="card kpi">
            <h3>Target Delta</h3>
            <strong>{dashboard ? `${Math.round(delta)} kcal` : "..."}</strong>
            <span>{delta > 0 ? "Above target" : "Below target"}</span>
          </article>

          <article className="card kpi">
            <h3>Workout Streak</h3>
            <strong>{dashboard ? `${dashboard.workout_streak}` : "..."}</strong>
            <span>Consecutive active days</span>
          </article>

          <article className="card kpi">
            <h3>Coach Signal</h3>
            <div className="signal-text">{dashboard?.motivation || "Loading..."}</div>
          </article>

          <form className="card form-card" id="goal-section" onSubmit={submitGoal}>
            <h3>Mission Profile</h3>
            <Field label="Goal">
              <select value={goalForm.goal} onChange={(e) => setGoalForm((f) => ({ ...f, goal: e.target.value }))}>
                <option value="fat_loss">fat_loss</option>
                <option value="maintenance">maintenance</option>
                <option value="muscle_gain">muscle_gain</option>
              </select>
            </Field>
            <Field label="Daily Calorie Target">
              <input
                type="number"
                value={goalForm.daily_calorie_target}
                onChange={(e) => setGoalForm((f) => ({ ...f, daily_calorie_target: e.target.value }))}
                placeholder="e.g. 2200"
              />
            </Field>
            <button type="submit">Apply Profile</button>
          </form>

          <form className="card form-card" id="workout-section" onSubmit={submitWorkout}>
            <h3>Log Training Session</h3>
            <Field label="Date"><input type="date" value={workoutForm.date} onChange={(e) => setWorkoutForm((f) => ({ ...f, date: e.target.value }))} /></Field>
            <Field label="Exercise"><input required value={workoutForm.exercise} onChange={(e) => setWorkoutForm((f) => ({ ...f, exercise: e.target.value }))} /></Field>
            <Field label="Sets"><input type="number" value={workoutForm.sets} onChange={(e) => setWorkoutForm((f) => ({ ...f, sets: e.target.value }))} /></Field>
            <Field label="Reps"><input type="number" value={workoutForm.reps} onChange={(e) => setWorkoutForm((f) => ({ ...f, reps: e.target.value }))} /></Field>
            <Field label="Weight"><input type="number" step="0.1" value={workoutForm.weight} onChange={(e) => setWorkoutForm((f) => ({ ...f, weight: e.target.value }))} /></Field>
            <Field label="Duration (Min)"><input type="number" value={workoutForm.duration_min} onChange={(e) => setWorkoutForm((f) => ({ ...f, duration_min: e.target.value }))} /></Field>
            <Field label="RPE"><input type="number" step="0.1" value={workoutForm.rpe} onChange={(e) => setWorkoutForm((f) => ({ ...f, rpe: e.target.value }))} /></Field>
            <Field label="Notes"><textarea value={workoutForm.notes} onChange={(e) => setWorkoutForm((f) => ({ ...f, notes: e.target.value }))} /></Field>
            <button type="submit">Commit Workout</button>
          </form>

          <form className="card form-card" id="meal-section" onSubmit={submitMeal}>
            <h3>Log Nutrition Intake</h3>
            <Field label="Date"><input type="date" value={mealForm.date} onChange={(e) => setMealForm((f) => ({ ...f, date: e.target.value }))} /></Field>
            <Field label="Meal Type">
              <select value={mealForm.meal_name} onChange={(e) => setMealForm((f) => ({ ...f, meal_name: e.target.value }))}>
                <option value="breakfast">breakfast</option>
                <option value="lunch">lunch</option>
                <option value="dinner">dinner</option>
                <option value="snack">snack</option>
              </select>
            </Field>
            <Field label="Foods">
              <textarea
                required
                placeholder="150g chicken breast, 180g rice, 1 banana"
                value={mealForm.description}
                onChange={(e) => setMealForm((f) => ({ ...f, description: e.target.value }))}
              />
            </Field>
            <button type="submit">Commit Meal</button>
          </form>

          <article className="card wide" id="plan-section">
            <h3>Adaptive Routine Output</h3>
            <div className="plan">{plan || "No adaptive output available."}</div>
          </article>

          <article className="card wide" id="history-section">
            <h3>Recent Workout Logs</h3>
            <div className="stack">
              {workouts.length === 0 ? (
                <div className="log-item">No workout logs yet.</div>
              ) : (
                workouts.slice(0, 12).map((w, i) => (
                  <div className="log-item" key={`${w.date}-${w.exercise}-${i}`}>
                    <strong>{w.date}</strong> | {w.exercise} | {w.sets}x{w.reps} @ {w.weight} | {w.duration_min} min | RPE {w.rpe}
                  </div>
                ))
              )}
            </div>
          </article>

          <article className="card full" id="recipe-section">
            <h3>Recipe Intelligence + Meal History</h3>
            <form onSubmit={findRecipes}>
              <Field label="Goal">
                <select value={recipeFilter.goal} onChange={(e) => setRecipeFilter((f) => ({ ...f, goal: e.target.value }))}>
                  <option value="">Use profile goal</option>
                  <option value="fat_loss">fat_loss</option>
                  <option value="maintenance">maintenance</option>
                  <option value="muscle_gain">muscle_gain</option>
                </select>
              </Field>
              <Field label="Meal Type">
                <select value={recipeFilter.meal_type} onChange={(e) => setRecipeFilter((f) => ({ ...f, meal_type: e.target.value }))}>
                  <option value="">any</option>
                  <option value="breakfast">breakfast</option>
                  <option value="lunch">lunch</option>
                  <option value="dinner">dinner</option>
                </select>
              </Field>
              <Field label="Max Calories">
                <input type="number" value={recipeFilter.max_calories} onChange={(e) => setRecipeFilter((f) => ({ ...f, max_calories: e.target.value }))} placeholder="optional" />
              </Field>
              <button type="submit">Run Recipe Scan</button>
            </form>

            <div className="layout" style={{ marginTop: "8px" }}>
              <div className="card" style={{ gridColumn: "span 6" }}>
                <h3>Recent Meals</h3>
                <div className="stack">
                  {meals.length === 0 ? (
                    <div className="log-item">No meals logged yet.</div>
                  ) : (
                    meals.slice(0, 10).map((m, i) => (
                      <div className="log-item" key={`${m.date}-${m.meal_name}-${i}`}>
                        <strong>{m.date}</strong> | {m.meal_name} | {Math.round(m.estimated_calories)} kcal
                        <div>{m.description}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
              <div className="card" style={{ gridColumn: "span 6" }}>
                <h3>Suggested Recipes</h3>
                <div className="stack">
                  {recipes.length === 0 ? (
                    <div className="log-item">No recipe match.</div>
                  ) : (
                    recipes.map((r) => (
                      <div className="log-item" key={r.name}>
                        <strong>{r.name}</strong> ({r.meal_type})
                        <div>{r.calories} kcal | P{r.protein_g} C{r.carbs_g} F{r.fat_g}</div>
                        <div>{r.ingredients.join(", ")}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </article>

          <article className="card full" id="android-section">
            <h3>NOX Android App</h3>
            <p className="notice">
              {ANDROID_APP_AVAILABLE
                ? "Android app is live. Download below."
                : "Android app is ready in project. Publish APK to web/downloads to enable this link."}
            </p>
            <a
              className="download-link"
              href={ANDROID_APP_AVAILABLE ? ANDROID_APP_URL : "#"}
              aria-disabled={ANDROID_APP_AVAILABLE ? "false" : "true"}
              onClick={(e) => {
                if (!ANDROID_APP_AVAILABLE) e.preventDefault();
              }}
            >
              {ANDROID_APP_AVAILABLE ? "Download NOX Android" : "Download NOX Android (Publishing Soon)"}
            </a>
          </article>
        </section>

        {loading && <p className="notice">Syncing local telemetry...</p>}
        {error && <p className="error">{error}</p>}
      </main>
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
