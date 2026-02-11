package com.nox.app

import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.content.SharedPreferences
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.motion.widget.MotionLayout
import androidx.core.content.ContextCompat
import androidx.core.widget.NestedScrollView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.bumptech.glide.Glide
import com.nox.app.data.NoxRepository
import com.nox.app.ui.MainViewModel
import com.nox.app.ui.MainViewModelFactory
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.time.LocalDate
import java.time.LocalDateTime

class MainActivity : AppCompatActivity() {
    private lateinit var api: ApiService
    private lateinit var prefs: SharedPreferences

    private lateinit var motionRoot: MotionLayout
    private var selectedProvider: String = "guest"
    private var activeUserName: String = ""

    private val viewModel: MainViewModel by viewModels {
        MainViewModelFactory(NoxRepository(api))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        setTheme(R.style.Theme_NOX)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences("nox_user_state", MODE_PRIVATE)

        api = Retrofit.Builder()
            .baseUrl(BuildConfig.NOX_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)

        motionRoot = findViewById(R.id.mainContent)

        setupHeroVisuals()
        setupQuickActions()
        setupScrollMotion()
        setupLoginUi()
        setupMicroInteractions()
        bindViewModel()
        runLoadingSequence()

        findViewById<Button>(R.id.refreshButton).setOnClickListener {
            viewModel.refreshDashboard(activeUserName)
        }
        findViewById<Button>(R.id.logWorkoutButton).setOnClickListener {
            logWorkout()
        }
        findViewById<Button>(R.id.logMealButton).setOnClickListener {
            logMeal()
        }
    }

    private fun bindViewModel() {
        val dashboardText = findViewById<TextView>(R.id.dashboardText)
        val statusText = findViewById<TextView>(R.id.statusText)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    dashboardText.text = state.dashboardSummary
                    statusText.text = state.status
                }
            }
        }
    }

    private fun runLoadingSequence() {
        val loadingOverlay = findViewById<View>(R.id.loadingOverlay)
        val loadingTitle = findViewById<TextView>(R.id.loadingTitle)
        val loadingPercent = findViewById<TextView>(R.id.loadingPercent)
        val loadingProgress = findViewById<ProgressBar>(R.id.loadingProgress)

        ObjectAnimator.ofFloat(loadingTitle, "alpha", 0.6f, 1f).apply {
            duration = 700
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.REVERSE
            start()
        }

        ValueAnimator.ofInt(0, 100).apply {
            duration = 2200
            interpolator = AccelerateDecelerateInterpolator()
            addUpdateListener { animator ->
                val value = animator.animatedValue as Int
                loadingPercent.text = "$value%"
                loadingProgress.progress = value
            }
            doOnEnd {
                loadingOverlay.visibility = View.GONE
                enterAppAfterLoading()
            }
            start()
        }
    }

    private fun setupLoginUi() {
        val googleBtn = findViewById<Button>(R.id.providerGoogleButton)
        val facebookBtn = findViewById<Button>(R.id.providerFacebookButton)
        val guestBtn = findViewById<Button>(R.id.providerGuestButton)
        val continueBtn = findViewById<Button>(R.id.continueButton)

        googleBtn.setOnClickListener { setProvider("google") }
        facebookBtn.setOnClickListener { setProvider("facebook") }
        guestBtn.setOnClickListener { setProvider("guest") }

        continueBtn.setOnClickListener {
            val nameInput = findViewById<EditText>(R.id.nameInput).text.toString().trim()
            if (nameInput.isBlank()) {
                viewModel.setStatus("Enter your name to continue")
                return@setOnClickListener
            }
            activeUserName = nameInput
            prefs.edit()
                .putString("active_user_name", activeUserName)
                .putString("active_provider", selectedProvider)
                .apply()
            showMainContent()
        }

        setProvider("guest")
    }

    private fun setProvider(provider: String) {
        selectedProvider = provider
        val googleBtn = findViewById<Button>(R.id.providerGoogleButton)
        val facebookBtn = findViewById<Button>(R.id.providerFacebookButton)
        val guestBtn = findViewById<Button>(R.id.providerGuestButton)

        val active = ContextCompat.getColor(this, R.color.nox_primary)
        val inactive = ContextCompat.getColor(this, R.color.nox_primary_dark)

        googleBtn.backgroundTintList = android.content.res.ColorStateList.valueOf(if (provider == "google") active else inactive)
        facebookBtn.backgroundTintList = android.content.res.ColorStateList.valueOf(if (provider == "facebook") active else inactive)
        guestBtn.backgroundTintList = android.content.res.ColorStateList.valueOf(if (provider == "guest") active else inactive)
    }

    private fun enterAppAfterLoading() {
        val savedName = prefs.getString("active_user_name", "") ?: ""
        val savedProvider = prefs.getString("active_provider", "guest") ?: "guest"

        if (savedName.isNotBlank()) {
            activeUserName = savedName
            selectedProvider = savedProvider
            showMainContent()
        } else {
            findViewById<View>(R.id.loginCard).visibility = View.VISIBLE
            motionRoot.visibility = View.GONE
        }
    }

    private fun showMainContent() {
        findViewById<View>(R.id.loginCard).visibility = View.GONE
        motionRoot.visibility = View.VISIBLE

        findViewById<TextView>(R.id.welcomeText).text = "${selectedProvider.uppercase()} | $activeUserName"
        viewModel.refreshDashboard(activeUserName)
    }

    private fun setupHeroVisuals() {
        val title = findViewById<TextView>(R.id.titleText)
        val tagline = findViewById<TextView>(R.id.taglineText)
        val scanLine = findViewById<View>(R.id.scanLine)

        val heroImage = findViewById<ImageView>(R.id.heroImage)
        val boltImage = findViewById<ImageView>(R.id.boltImage)
        val cbumImage = findViewById<ImageView>(R.id.cbumImage)
        val phelpsImage = findViewById<ImageView>(R.id.phelpsImage)

        Glide.with(this)
            .load("file:///android_asset/athletes/michael-phelps.jpg")
            .centerCrop()
            .placeholder(R.drawable.ic_nox_logo)
            .error(R.drawable.ic_nox_logo)
            .into(heroImage)

        Glide.with(this)
            .load("file:///android_asset/athletes/usain-bolt.jpg")
            .centerCrop()
            .placeholder(R.drawable.ic_nox_logo)
            .error(R.drawable.ic_nox_logo)
            .into(boltImage)

        Glide.with(this)
            .load("file:///android_asset/athletes/chris-bumstead.jpg")
            .centerCrop()
            .placeholder(R.drawable.ic_nox_logo)
            .error(R.drawable.ic_nox_logo)
            .into(cbumImage)

        Glide.with(this)
            .load("file:///android_asset/athletes/michael-phelps.jpg")
            .centerCrop()
            .placeholder(R.drawable.ic_nox_logo)
            .error(R.drawable.ic_nox_logo)
            .into(phelpsImage)

        ObjectAnimator.ofFloat(title, "alpha", 0.76f, 1f).apply {
            duration = 1050
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
            interpolator = AccelerateDecelerateInterpolator()
            start()
        }

        ObjectAnimator.ofFloat(tagline, "translationX", -8f, 8f).apply {
            duration = 1850
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
            interpolator = AccelerateDecelerateInterpolator()
            start()
        }

        ObjectAnimator.ofFloat(scanLine, "translationX", -130f, 280f).apply {
            duration = 1900
            repeatMode = ValueAnimator.RESTART
            repeatCount = ValueAnimator.INFINITE
            start()
        }

        ObjectAnimator.ofFloat(findViewById<View>(R.id.heroLottie), "rotation", 0f, 8f, 0f).apply {
            duration = 3000
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.REVERSE
            start()
        }
    }

    private fun setupQuickActions() {
        val dashboardCard = findViewById<View>(R.id.dashboardCard)
        val workoutCard = findViewById<View>(R.id.workoutCard)
        val mealCard = findViewById<View>(R.id.mealCard)
        val actionDashboard = findViewById<Button>(R.id.actionDashboard)
        val actionWorkout = findViewById<Button>(R.id.actionWorkout)
        val actionMeal = findViewById<Button>(R.id.actionMeal)
        val opsTicker = findViewById<TextView>(R.id.opsTicker)
        val rootScroll = findViewById<NestedScrollView>(R.id.rootScroll)

        actionDashboard.setOnClickListener {
            activateModule("dashboard", rootScroll, dashboardCard, workoutCard, mealCard)
            highlightAction(actionDashboard, actionWorkout, actionMeal)
        }
        actionWorkout.setOnClickListener {
            activateModule("workout", rootScroll, dashboardCard, workoutCard, mealCard)
            highlightAction(actionWorkout, actionDashboard, actionMeal)
        }
        actionMeal.setOnClickListener {
            activateModule("meal", rootScroll, dashboardCard, workoutCard, mealCard)
            highlightAction(actionMeal, actionDashboard, actionWorkout)
        }

        val actionButtons = listOf(actionDashboard, actionWorkout, actionMeal)
        actionButtons.forEachIndexed { idx, button ->
            ObjectAnimator.ofFloat(button, "translationY", 0f, -4f, 0f).apply {
                duration = 1700 + (idx * 180L)
                repeatMode = ValueAnimator.RESTART
                repeatCount = ValueAnimator.INFINITE
                startDelay = (idx * 140L)
                start()
            }
        }

        opsTicker.isSelected = true
        ObjectAnimator.ofFloat(opsTicker, "alpha", 0.66f, 1f).apply {
            duration = 900
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
            start()
        }

        activateModule("dashboard", rootScroll, dashboardCard, workoutCard, mealCard)
        highlightAction(actionDashboard, actionWorkout, actionMeal)
    }

    private fun setupScrollMotion() {
        val rootScroll = findViewById<NestedScrollView>(R.id.rootScroll)
        val title = findViewById<TextView>(R.id.titleText)
        val altTitle = findViewById<TextView>(R.id.titleAltText)
        val tagline = findViewById<TextView>(R.id.taglineText)

        rootScroll.setOnScrollChangeListener { _, _, scrollY, _, _ ->
            val progress = (scrollY / 420f).coerceIn(0f, 1f)
            motionRoot.progress = progress
            altTitle.alpha = progress
            title.alpha = 1f - (progress * 0.55f)
            tagline.alpha = 1f - (progress * 0.45f)
        }

        ObjectAnimator.ofFloat(title, "letterSpacing", 0.03f, 0.12f, 0.03f).apply {
            duration = 2200
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
            start()
        }
    }

    private fun setupMicroInteractions() {
        val buttons = listOf(
            R.id.refreshButton,
            R.id.logWorkoutButton,
            R.id.logMealButton,
            R.id.actionDashboard,
            R.id.actionWorkout,
            R.id.actionMeal,
            R.id.continueButton,
            R.id.providerGoogleButton,
            R.id.providerFacebookButton,
            R.id.providerGuestButton
        )

        buttons.forEach { id ->
            findViewById<Button>(id).setOnTouchListener { view, event ->
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> {
                        view.animate().scaleX(0.96f).scaleY(0.96f).setDuration(90).start()
                    }
                    MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                        view.animate().scaleX(1f).scaleY(1f).setDuration(120).start()
                    }
                }
                false
            }
        }
    }

    private fun activateModule(
        module: String,
        scroll: NestedScrollView,
        dashboardCard: View,
        workoutCard: View,
        mealCard: View
    ) {
        val cards = mapOf(
            "dashboard" to dashboardCard,
            "workout" to workoutCard,
            "meal" to mealCard
        )
        cards.forEach { (name, view) ->
            if (name == module) {
                view.visibility = View.VISIBLE
                view.alpha = 0f
                view.translationY = 24f
                view.animate()
                    .alpha(1f)
                    .translationY(0f)
                    .setDuration(280)
                    .setInterpolator(AccelerateDecelerateInterpolator())
                    .start()
            } else {
                view.visibility = View.GONE
            }
        }
        scroll.post { scroll.smoothScrollTo(0, 0) }
    }

    private fun highlightAction(active: Button, firstInactive: Button, secondInactive: Button) {
        active.scaleX = 1.06f
        active.scaleY = 1.06f
        firstInactive.scaleX = 1.0f
        firstInactive.scaleY = 1.0f
        secondInactive.scaleX = 1.0f
        secondInactive.scaleY = 1.0f
    }

    private fun logWorkout() {
        val exercise = findViewById<EditText>(R.id.workoutExerciseInput).text.toString().trim()
        val sets = findViewById<EditText>(R.id.workoutSetsInput).text.toString().toIntOrNull() ?: 0
        val reps = findViewById<EditText>(R.id.workoutRepsInput).text.toString().toIntOrNull() ?: 0
        val weight = findViewById<EditText>(R.id.workoutWeightInput).text.toString().toDoubleOrNull() ?: 0.0
        val rpe = findViewById<EditText>(R.id.workoutRpeInput).text.toString().toDoubleOrNull() ?: 7.0
        val duration = findViewById<EditText>(R.id.workoutDurationInput).text.toString().toIntOrNull() ?: 0
        val notes = findViewById<EditText>(R.id.workoutNotesInput).text.toString().trim()

        if (exercise.isBlank()) {
            viewModel.setStatus("Workout error: exercise is required")
            return
        }

        val req = WorkoutRequest(
            date = LocalDate.now().toString(),
            exercise = exercise,
            sets = sets,
            reps = reps,
            weight = weight,
            duration_min = duration,
            rpe = rpe,
            notes = notes,
            user_name = activeUserName,
            provider = selectedProvider
        )

        viewModel.logWorkout(req, activeUserName)
        saveLocalUserEntry(
            type = "workout",
            payload = JSONObject()
                .put("exercise", exercise)
                .put("sets", sets)
                .put("reps", reps)
                .put("weight", weight)
                .put("duration_min", duration)
                .put("rpe", rpe)
                .put("notes", notes)
        )
        clearWorkoutInputs()
    }

    private fun logMeal() {
        val mealName = findViewById<EditText>(R.id.mealNameInput).text.toString().trim()
        val description = findViewById<EditText>(R.id.mealDescriptionInput).text.toString().trim()

        if (mealName.isBlank() || description.isBlank()) {
            viewModel.setStatus("Meal error: meal name and description are required")
            return
        }

        val req = MealRequest(
            date = LocalDate.now().toString(),
            meal_name = mealName,
            description = description,
            user_name = activeUserName,
            provider = selectedProvider
        )

        viewModel.logMeal(req, activeUserName)
        saveLocalUserEntry(
            type = "meal",
            payload = JSONObject()
                .put("meal_name", mealName)
                .put("description", description)
        )
        clearMealInputs()
    }

    private fun saveLocalUserEntry(type: String, payload: JSONObject) {
        if (activeUserName.isBlank()) return
        val key = "entries_${activeUserName.lowercase().replace(" ", "_")}" 
        val existing = prefs.getString(key, "[]") ?: "[]"
        val arr = JSONArray(existing)
        val entry = JSONObject()
            .put("type", type)
            .put("provider", selectedProvider)
            .put("timestamp", LocalDateTime.now().toString())
            .put("payload", payload)
        arr.put(entry)
        prefs.edit().putString(key, arr.toString()).apply()
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

    private fun ValueAnimator.doOnEnd(action: () -> Unit) {
        addListener(object : android.animation.Animator.AnimatorListener {
            override fun onAnimationStart(animation: android.animation.Animator) {}
            override fun onAnimationEnd(animation: android.animation.Animator) = action()
            override fun onAnimationCancel(animation: android.animation.Animator) {}
            override fun onAnimationRepeat(animation: android.animation.Animator) {}
        })
    }
}
