package com.nox.app.data

import com.nox.app.ApiService
import com.nox.app.DashboardResponse
import com.nox.app.GenericResponse
import com.nox.app.MealRequest
import com.nox.app.WorkoutRequest

class NoxRepository(private val api: ApiService) {
    suspend fun fetchDashboard(): Result<DashboardResponse> = runCatching {
        api.getDashboard()
    }

    suspend fun logWorkout(request: WorkoutRequest): Result<GenericResponse> = runCatching {
        api.logWorkout(request)
    }

    suspend fun logMeal(request: MealRequest): Result<GenericResponse> = runCatching {
        api.logMeal(request)
    }
}
