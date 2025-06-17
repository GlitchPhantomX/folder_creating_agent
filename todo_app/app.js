document.addEventListener('DOMContentLoaded', function () {
    // --- Variables ---
    const taskInput = document.getElementById('taskInput');
    const addButton = document.getElementById('addButton');
    const taskList = document.querySelector('.task-list ul');
    const filters = document.querySelector('.filters');
    const taskCounter = document.getElementById('counter');

    let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

    // --- Functions ---
    function updateTaskCounter() {
        taskCounter.innerText = tasks.filter(task => !task.completed).length;
    }

    function saveTasks() {
        localStorage.setItem('tasks', JSON.stringify(tasks));
    }

    function renderTasks() {
        taskList.innerHTML = '';
        tasks.forEach((task, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <input type="checkbox" data-index="${index}" id="task-${index}" ${task.completed ? 'checked' : ''}>
                <label for="task-${index}" class="task-text ${task.completed ? 'completed' : ''}">${task.text}</label>
                <button class="edit-button" data-index="${index}">Edit</button>
                <button class="delete-button" data-index="${index}">Delete</button>
            `;
            taskList.appendChild(li);
        });
        updateTaskCounter();
    }

    function addTask() {
        const taskText = taskInput.value.trim();
        if (taskText !== '') {
            tasks.push({ text: taskText, completed: false });
            taskInput.value = '';
            saveTasks();
            renderTasks();
        }
    }

    function deleteTask(index) {
        tasks.splice(index, 1);
        saveTasks();
        renderTasks();
    }

    function editTask(index) {
        const task = tasks[index];
        const newText = prompt('Edit task', task.text);
        if (newText !== null && newText.trim() !== '') {
            task.text = newText.trim();
            saveTasks();
            renderTasks();
        }
    }

    function toggleComplete(index) {
        tasks[index].completed = !tasks[index].completed;
        saveTasks();
        renderTasks();
    }

    function filterTasks(filter) {
        let filteredTasks = [];
        switch (filter) {
            case 'active':
                filteredTasks = tasks.filter(task => !task.completed);
                break;
            case 'completed':
                filteredTasks = tasks.filter(task => task.completed);
                break;
            default:
                filteredTasks = tasks;
        }

        taskList.innerHTML = '';
        filteredTasks.forEach((task, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <input type="checkbox" data-index="${index}" id="task-${index}" ${task.completed ? 'checked' : ''}>
                <label for="task-${index}" class="task-text ${task.completed ? 'completed' : ''}">${task.text}</label>
                <button class="edit-button" data-index="${index}">Edit</button>
                <button class="delete-button" data-index="${index}">Delete</button>
            `;
            taskList.appendChild(li);
        });
    }

    // --- Event Listeners ---
    addButton.addEventListener('click', addTask);

    taskInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            addTask();
        }
    });

    taskList.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-button')) {
            const index = event.target.dataset.index;
            deleteTask(index);
        }
        if (event.target.classList.contains('edit-button')) {
            const index = event.target.dataset.index;
            editTask(index);
        }
        if (event.target.matches('input[type="checkbox"]')) {
            const index = event.target.dataset.index;
            toggleComplete(index);
        }
    });

    filters.addEventListener('click', function (event) {
        if (event.target.tagName === 'BUTTON') {
            document.querySelectorAll('.filters button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            filterTasks(event.target.dataset.filter);
        }
    });

    // --- Initialization ---
    renderTasks();
});