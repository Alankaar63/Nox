package com.nox.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.nox.app.MealRequest
import com.nox.app.WorkoutRequest
import com.nox.app.data.NoxRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class MainViewModel(private val repository: NoxRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    fun refreshDashboard(activeUserName: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(status = "Syncing dashboard...") }
            repository.fetchDashboard()
                .onSuccess { dash ->
                    val summary = buildString {
                        appendLine("Date: ${dash.date}")
                        appendLine("Goal: ${dash.profile.goal}")
                        appendLine("Daily target: ${dash.profile.daily_calorie_target} kcal")
                        appendLine("Calories today: ${dash.calories_today.toInt()} kcal")
                        appendLine("Workout streak: ${dash.workout_streak} day(s)")
                        append("Coach signal: ${dash.motivation}")
                    }
                    _uiState.update {
                        it.copy(
                            dashboardSummary = summary,
                            status = "Dashboard synced${if (activeUserName.isNotBlank()) " | user: $activeUserName" else ""}"
                        )
                    }
                }
                .onFailure { err ->
                    _uiState.update { it.copy(status = "Dashboard error: ${err.message}") }
                }
        }
    }

    fun logWorkout(request: WorkoutRequest, activeUserName: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(status = "Logging workout...") }
            repository.logWorkout(request)
                .onSuccess {
                    _uiState.update {
                        it.copy(status = "Workout logged${if (activeUserName.isNotBlank()) " for $activeUserName" else ""}")
                    }
                }
                .onFailure { err ->
                    _uiState.update { it.copy(status = "Workout error: ${err.message}") }
                }
        }
    }

    fun logMeal(request: MealRequest, activeUserName: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(status = "Logging meal...") }
            repository.logMeal(request)
                .onSuccess {
                    _uiState.update {
                        it.copy(status = "Meal logged${if (activeUserName.isNotBlank()) " for $activeUserName" else ""}")
                    }
                }
                .onFailure { err ->
                    _uiState.update { it.copy(status = "Meal error: ${err.message}") }
                }
        }
    }

    fun setStatus(message: String) {
        _uiState.update { it.copy(status = message) }
    }
}

class MainViewModelFactory(private val repository: NoxRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return MainViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class: ${modelClass.name}")
    }
}
