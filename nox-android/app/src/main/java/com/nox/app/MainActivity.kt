package com.nox.app

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.time.LocalDate

class MainActivity : AppCompatActivity() {
    private lateinit var api: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        setTheme(R.style.Theme_NOX)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        api = Retrofit.Builder()
            .baseUrl(BuildConfig.NOX_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)

        val dashboardText = findViewById<TextView>(R.id.dashboardText)
        val statusText = findViewById<TextView>(R.id.statusText)

        val refreshButton = findViewById<Button>(R.id.refreshButton)
        val logWorkoutButton = findViewById<Button>(R.id.logWorkoutButton)
        val logMealButton = findViewById<Button>(R.id.logMealButton)

        refreshButton.setOnClickListener {
            refreshDashboard(dashboardText, statusText)
        }

        logWorkoutButton.setOnClickListener {
            logWorkout(statusText)
        }

        logMealButton.setOnClickListener {
            logMeal(statusText)
        }

        refreshDashboard(dashboardText, statusText)
    }

    private fun refreshDashboard(dashboardText: TextView, statusText: TextView) {
        lifecycleScope.launch {
            statusText.text = "Fetching dashboard..."
            runCatching {
                api.getDashboard()
            }.onSuccess { dash ->
                dashboardText.text = buildString {
                    appendLine("Date: ${dash.date}")
                    appendLine("Goal: ${dash.profile.goal}")
                    appendLine("Daily target: ${dash.profile.daily_calorie_target} kcal")
                    appendLine("Calories today: ${dash.calories_today.toInt()} kcal")
                    appendLine("Workout streak: ${dash.workout_streak} day(s)")
                    append("Motivation: ${dash.motivation}")
                }
                statusText.text = "Dashboard synced"
            }.onFailure { e ->
                statusText.text = "Dashboard error: ${e.message}"
            }
        }
    }

    private fun logWorkout(statusText: TextView) {
        val exercise = findViewById<EditText>(R.id.workoutExerciseInput).text.toString().trim()
        val sets = findViewById<EditText>(R.id.workoutSetsInput).text.toString().toIntOrNull() ?: 0
        val reps = findViewById<EditText>(R.id.workoutRepsInput).text.toString().toIntOrNull() ?: 0
        val weight = findViewById<EditText>(R.id.workoutWeightInput).text.toString().toDoubleOrNull() ?: 0.0
        val rpe = findViewById<EditText>(R.id.workoutRpeInput).text.toString().toDoubleOrNull() ?: 7.0
        val duration = findViewById<EditText>(R.id.workoutDurationInput).text.toString().toIntOrNull() ?: 0
        val notes = findViewById<EditText>(R.id.workoutNotesInput).text.toString().trim()

        if (exercise.isBlank()) {
            statusText.text = "Workout error: exercise is required"
            return
        }

        lifecycleScope.launch {
            statusText.text = "Logging workout..."
            val req = WorkoutRequest(
                date = LocalDate.now().toString(),
                exercise = exercise,
                sets = sets,
                reps = reps,
                weight = weight,
                duration_min = duration,
                rpe = rpe,
                notes = notes
            )
            runCatching {
                api.logWorkout(req)
            }.onSuccess {
                statusText.text = "Workout logged"
                clearWorkoutInputs()
            }.onFailure { e ->
                statusText.text = "Workout error: ${e.message}"
            }
        }
    }

    private fun logMeal(statusText: TextView) {
        val mealName = findViewById<EditText>(R.id.mealNameInput).text.toString().trim()
        val description = findViewById<EditText>(R.id.mealDescriptionInput).text.toString().trim()

        if (mealName.isBlank() || description.isBlank()) {
            statusText.text = "Meal error: meal name and description are required"
            return
        }

        lifecycleScope.launch {
            statusText.text = "Logging meal..."
            val req = MealRequest(
                date = LocalDate.now().toString(),
                meal_name = mealName,
                description = description
            )
            runCatching {
                api.logMeal(req)
            }.onSuccess {
                statusText.text = "Meal logged"
                clearMealInputs()
            }.onFailure { e ->
                statusText.text = "Meal error: ${e.message}"
            }
        }
    }

    private fun clearWorkoutInputs() {
        findViewById<EditText>(R.id.workoutExerciseInput).text.clear()
        findViewById<EditText>(R.id.workoutSetsInput).text.clear()
        findViewById<EditText>(R.id.workoutRepsInput).text.clear()
        findViewById<EditText>(R.id.workoutWeightInput).text.clear()
        findViewById<EditText>(R.id.workoutRpeInput).text.clear()
        findViewById<EditText>(R.id.workoutDurationInput).text.clear()
        findViewById<EditText>(R.id.workoutNotesInput).text.clear()
    }

    private fun clearMealInputs() {
        findViewById<EditText>(R.id.mealNameInput).text.clear()
        findViewById<EditText>(R.id.mealDescriptionInput).text.clear()
    }
}
