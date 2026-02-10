import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val keystoreProps = Properties()
val keystorePropsFile = rootProject.file("keystore.properties")
if (keystorePropsFile.exists()) {
    keystorePropsFile.inputStream().use { keystoreProps.load(it) }
}

val enableReleaseSigning =
    ((project.findProperty("NOX_ENABLE_RELEASE_SIGNING") as? String)?.toBooleanStrictOrNull() ?: false)

android {
    namespace = "com.nox.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.nox.app"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        val baseUrl = (project.findProperty("NOX_BASE_URL") as? String) ?: "http://10.0.2.2:8080/"
        buildConfigField("String", "NOX_BASE_URL", "\"$baseUrl\"")
    }

    signingConfigs {
        if (enableReleaseSigning && keystorePropsFile.exists()) {
            val storeFilePath = keystoreProps.getProperty("storeFile", "")
            val ksStorePassword = keystoreProps.getProperty("storePassword", "")
            val ksKeyAlias = keystoreProps.getProperty("keyAlias", "")
            val ksKeyPassword = keystoreProps.getProperty("keyPassword", "")
            val storeFileObj = file(storeFilePath)

            if (storeFilePath.isNotBlank() && storeFileObj.exists() && ksStorePassword.isNotBlank() && ksKeyAlias.isNotBlank()) {
                create("release") {
                    storeFile = storeFileObj
                    storePassword = ksStorePassword
                    keyAlias = ksKeyAlias
                    keyPassword = ksKeyPassword
                    enableV1Signing = true
                    enableV2Signing = true
                }
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // Default to debug signing for frictionless builds; turn on release signing explicitly.
            signingConfig = signingConfigs.findByName("release") ?: signingConfigs.getByName("debug")
        }
        debug {
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-gson:2.11.0")
}
