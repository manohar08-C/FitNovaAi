setTimeout(() => {
    const flash = document.getElementById("flash-container");
    if (flash) {
        flash.style.transition = "opacity 0.5s ease";
        flash.style.opacity = "0";
        setTimeout(() => {
            flash.remove();
        }, 500);
    }
}, 3000);


function toggleTheme() {
    document.body.classList.toggle("light-mode");
}

function startWorkout() {
    const exercise = document.getElementById("exerciseSelect").value;

    fetch("/start_workout", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "exercise=" + exercise
    });
}

function stopWorkout() {
    fetch("/stop_workout", {
        method: "POST"
    }).then(() => {
        const img = document.querySelector("img");
        img.src = "";
    });
}



