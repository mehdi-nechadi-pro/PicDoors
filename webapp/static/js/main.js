document.addEventListener("DOMContentLoaded", function() {
    const imgElement = document.getElementById("videoStream");
    const placeholder = document.getElementById("placeholder");
    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const statusText = document.getElementById("statusText");

    // Récupération de l'URL Flask depuis l'attribut HTML
    const streamUrl = imgElement.getAttribute("data-url");

    startBtn.addEventListener("click", function() {
        // Ajout timestamp pour éviter le cache navigateur
        imgElement.src = streamUrl + "?t=" + new Date().getTime();
        
        imgElement.style.display = "block";
        placeholder.style.display = "none";
        
        startBtn.disabled = true;
        startBtn.classList.add("opacity-50");
        stopBtn.disabled = false;
        stopBtn.classList.remove("opacity-50");
        
        statusText.innerText = "Analyse en cours...";
        statusText.style.color = "#0f0";
    });

    stopBtn.addEventListener("click", function() {
        imgElement.src = ""; // Coupe la connexion
        
        imgElement.style.display = "none";
        placeholder.style.display = "block";
        
        startBtn.disabled = false;
        startBtn.classList.remove("opacity-50");
        stopBtn.disabled = true;
        stopBtn.classList.add("opacity-50");
        
        statusText.innerText = "Flux coupé (Serveur actif)";
        statusText.style.color = "#666";
    });
});