const qs = (selector) => document.querySelector(selector);
let filter = 'all';

function request(url, options = {}) {
  return fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
  }).then(async response => {
    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      try { message = (await response.json()).detail || message; } catch (_) {}
      throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
    }
    return response.status === 204 ? null : response.json();
  });
}

function make(tag, className = '', text = '') {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text) el.textContent = text;
  return el;
}

function taskElement(task) {
  const row = make('div', `task-row${task.completed ? ' done' : ''}`);
  const toggle = make('button', 'task-toggle', task.completed ? '✓' : '');
  toggle.type = 'button';
  toggle.setAttribute('aria-label', task.completed ? 'Mark task incomplete' : 'Mark task complete');
  toggle.addEventListener('click', async () => {
    try { await request(`/api/tasks/${task.id}`, { method: 'PATCH', body: JSON.stringify({ completed: !task.completed }) }); await load(); }
    catch (error) { alert(error.message); }
  });
  const content = make('div', 'task-content');
  content.appendChild(make('div', 'task-name', task.title));
  const metadata = make('div', 'task-meta');
  metadata.appendChild(make('span', `tag ${['Study', 'Project', 'Assignment', 'Personal'].includes(task.category) ? task.category : ''}`, task.category));
  metadata.appendChild(make('span', `priority ${task.priority}`, task.priority));
  if (task.due_date) metadata.appendChild(make('span', 'task-date', `◷ ${task.due_date}`));
  content.appendChild(metadata);
  const remove = make('button', 'delete-button', '×');
  remove.type = 'button'; remove.setAttribute('aria-label', `Delete ${task.title}`);
  remove.addEventListener('click', async () => {
    if (!confirm(`Delete "${task.title}"?`)) return;
    try { await request(`/api/tasks/${task.id}`, { method: 'DELETE' }); await load(); }
    catch (error) { alert(error.message); }
  });
  row.append(toggle, content, remove);
  return row;
}

async function load() {
  const [tasks, stats] = await Promise.all([request(`/api/tasks?status=${filter}`), request('/api/stats')]);
  qs('#total').textContent = stats.total;
  qs('#pending').textContent = stats.pending;
  qs('#done').textContent = stats.done;
  const list = qs('#task-list'); list.replaceChildren();
  if (!tasks.length) list.appendChild(make('div', 'empty', 'No tasks here yet. Create your first one!'));
  tasks.forEach(task => list.appendChild(taskElement(task)));
}

qs('#today').textContent = new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' }).format(new Date());
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', async () => {
  filter = button.dataset.filter;
  document.querySelectorAll('[data-filter]').forEach(b => b.classList.toggle('active', b === button));
  await load().catch(error => { qs('#task-list').textContent = error.message; });
}));
qs('#task-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = {
    title: qs('#title').value.trim(),
    category: qs('#category').value,
    priority: qs('#priority').value,
    due_date: qs('#due_date').value || null
  };
  if (!payload.title) return;
  qs('#form-error').textContent = '';
  try { await request('/api/tasks', { method: 'POST', body: JSON.stringify(payload) }); form.reset(); filter = 'all'; document.querySelectorAll('[data-filter]').forEach(b => b.classList.toggle('active', b.dataset.filter === filter)); await load(); }
  catch (error) { qs('#form-error').textContent = error.message; }
});
load().catch(error => { qs('#task-list').textContent = `Could not connect to the server: ${error.message}`; });
