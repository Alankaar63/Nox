package com.nox.app

data class DashboardResponse(
    val date: String,
    val profile: Profile,
    val calories_today: Double,
    val workout_streak: Int,
    val motivation: String
)

data class Profile(
    val name: String,
    val goal: String,
    val daily_calorie_target: Int
)

data class WorkoutRequest(
    val date: String,
    val exercise: String,
    val sets: Int,
    val reps: Int,
    val weight: Double,
    val duration_min: Int,
    val rpe: Double,
    val notes: String,
    val user_name: String? = null,
    val provider: String? = null
)

data class MealRequest(
    val date: String,
    val meal_name: String,
    val description: String,
    val user_name: String? = null,
    val provider: String? = null
)

data class GenericResponse(
    val ok: Boolean = false,
    val error: String? = null
)
