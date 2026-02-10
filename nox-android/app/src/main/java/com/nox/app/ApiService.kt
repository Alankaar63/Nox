package com.nox.app

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {
    @GET("api/dashboard")
    suspend fun getDashboard(): DashboardResponse

    @POST("api/workouts")
    suspend fun logWorkout(@Body body: WorkoutRequest): GenericResponse

    @POST("api/meals")
    suspend fun logMeal(@Body body: MealRequest): GenericResponse
}
