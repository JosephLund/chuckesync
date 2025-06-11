document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    slotMinTime: "06:00:00",
    slotMaxTime: "24:00:00",
    allDaySlot: false,
    selectable: false,
    editable: false,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'timeGridDay,timeGridWeek'
    },
    buttonText: {
      today: 'Today',
      week: 'Week',
      day: 'Day'
    },
    aspectRatio: 1.8,
    expandRows: true,
  });

  calendar.render();
  window.calendar = calendar;

  // Load stores and shifts after calendar is ready
  loadStores().then(loadShifts);
  document.getElementById('storeSelect').addEventListener('change', loadShifts);

  // Sidebar hamburger menu toggle
  document.getElementById('menu-toggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });
});

async function loadStores() {
  console.log("Loading stores...");
  const response = await fetch('/api/stores');
  const stores = await response.json();

  const storeSelect = document.getElementById('storeSelect');
  storeSelect.innerHTML = '<option value="">All Stores</option>';

  stores.forEach(store => {
    const option = document.createElement('option');
    option.value = store.id;
    option.textContent = `${store.number} - ${store.name}`;
    storeSelect.appendChild(option);
  });
}

async function loadShifts() {
  console.log("Loading shifts...");
  const storeId = document.getElementById('storeSelect').value;
  const url = storeId ? `/api/shifts?store_id=${storeId}` : '/api/shifts';
  const response = await fetch(url);
  const shifts = await response.json();

  const events = shifts.map(shift => {
    return {
      id: shift.id,
      title: `${shift.start_time} - ${shift.end_time} (${shift.store_name})`,
      start: `${shift.date}T${shift.start_time}:00`,
      end: `${shift.date}T${shift.end_time}:00`
    };
  });

  window.calendar.removeAllEvents();
  window.calendar.addEventSource(events);
}
