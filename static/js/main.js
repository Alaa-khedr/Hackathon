document.addEventListener("DOMContentLoaded", () => {
    const startButton = document.getElementById("startRecording");
    const stopButton = document.getElementById("stopRecording");
    const outputDiv = document.getElementById("output");
    const fileInput = document.getElementById("fileInput");
    const uploadButton = document.getElementById("uploadButton");
    const searchButton = document.getElementById("searchButton");
    const searchInput = document.getElementById("searchInput");
    const clearSearchButton = document.getElementById("clearSearchButton");

    const currentTasksDiv = document.getElementById("currentTasks");
    const originalTasks = currentTasksDiv.innerHTML;
    let isSearching = false;

    let tasks = [];

    function moveTask(taskElement, destination) {
        const completedTasksDiv = document.getElementById("completedTasks");

        if (destination === "completed") {
            completedTasksDiv.appendChild(taskElement);
        } else {
            currentTasksDiv.appendChild(taskElement);
        }
    }

    function handleResponse(data) {
        const taskLabel = document.createElement("label");
        const taskCheckbox = document.createElement("input");
        taskCheckbox.type = "checkbox";
        taskCheckbox.className = "task-checkbox";

        taskLabel.className = "task-label";
        taskLabel.appendChild(taskCheckbox);
        taskLabel.appendChild(document.createTextNode(data.text));

        currentTasksDiv.appendChild(taskLabel);
    }

    function handleError(error) {
        console.error("Error:", error);
        outputDiv.textContent = "An error occurred."; // Handle error in the UI
    }

    uploadButton.addEventListener("click", () => {
        const file = fileInput.files[0]; // Get the selected file

        if (file) {
            const formData = new FormData();
            formData.append("file", file);

            fetch("/upload-and-convert", {
                method: "POST",
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                handleResponse(data);
            })
            .catch(error => {
                handleError(error);
            });
        }
    });

    startButton.addEventListener("click", () => {
        startButton.disabled = true;
        stopButton.disabled = false;

        outputDiv.textContent = "Please wait, the conversion may take some time...";

        fetch("/start-recording")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                handleResponse(data);
            })
            .catch(error => {
                handleError(error);
            });
    });

    stopButton.addEventListener("click", () => {
        startButton.disabled = false;
        stopButton.disabled = true;
    });

    document.addEventListener("change", (event) => {
        if (event.target.type === "checkbox") {
            const taskLabel = event.target.parentNode;
            const destination = event.target.checked ? "completed" : "current";
            moveTask(taskLabel, destination);
        }
    });

    searchButton.addEventListener("click", () => {
        const searchTerm = searchInput.value.trim().toLowerCase();
        if (searchTerm === "") {
            return;
        }

        searchTasks(searchTerm);
    });

    clearSearchButton.addEventListener("click", () => { // Modify this event listener
        clearSearch();
    });


    function clearSearch() {
        currentTasksDiv.innerHTML = originalTasks;
        isSearching = false; // Reset the search flag
    }

    function searchTasks(searchTerm) {
        const tasks = document.getElementsByClassName("task-label");
        for (const task of tasks) {
            const taskText = task.textContent.toLowerCase();
            const highlightedText = taskText.replace(
                new RegExp(`\\b${searchTerm}\\b`, "gi"),
                match => `<span class="highlighted-word">${match}</span>`
            );
            task.innerHTML = highlightedText;

            // Preserve checkboxes during search
            task.innerHTML = `<input type="checkbox" class="task-checkbox">${highlightedText}`;
        }
        isSearching = true; // Set the search flag
    }
});
