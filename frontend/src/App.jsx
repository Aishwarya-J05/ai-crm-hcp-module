import { useEffect } from "react";
import { Activity, BrainCircuit, CalendarClock, FileText, FlaskConical, Save, Search, Send, Sparkles } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";

import { applySuggestion, fetchInteractions, resetForm, sendChatMessage, submitInteraction, updateField } from "./features/interactions/interactionsSlice.js";

const followUps = [
  "Schedule follow-up meeting in 2 weeks",
  "Send OncoBoost Phase III PDF",
  "Invite HCP to regional advisory board",
];

export function App() {
  const dispatch = useDispatch();
  const { chat, error, form, items, lastTool, status } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  function onChange(event) {
    dispatch(updateField({ name: event.target.name, value: event.target.value }));
  }

  function onSubmit(event) {
    event.preventDefault();
    dispatch(submitInteraction(form));
  }

  function onChat(event) {
    event.preventDefault();
    const input = new FormData(event.currentTarget).get("message").trim();
    if (!input) return;
    dispatch(sendChatMessage(input)).then(() => dispatch(fetchInteractions()));
    event.currentTarget.reset();
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">HCP CRM</p>
          <h1>Log HCP Interaction</h1>
        </div>
        <div className="agent-status">
          <BrainCircuit size={18} />
          <span>{lastTool ? `Last tool: ${lastTool}` : "LangGraph agent ready"}</span>
        </div>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="workspace">
        <form className="panel interaction-form" onSubmit={onSubmit}>
          <div className="panel-header">
            <FileText size={18} />
            <span>Interaction Details</span>
          </div>

          <div className="grid two">
            <label>
              <span>HCP Name</span>
              <input name="hcp_name" value={form.hcp_name} onChange={onChange} placeholder="Search or select HCP..." required />
            </label>
            <label>
              <span>Interaction Type</span>
              <select name="interaction_type" value={form.interaction_type} onChange={onChange}>
                <option>Meeting</option>
                <option>Call</option>
                <option>Email</option>
                <option>Conference</option>
              </select>
            </label>
            <label>
              <span>Date</span>
              <input type="date" name="interaction_date" value={form.interaction_date} onChange={onChange} required />
            </label>
            <label>
              <span>Time</span>
              <input type="time" name="interaction_time" value={form.interaction_time} onChange={onChange} required />
            </label>
          </div>

          <label>
            <span>Attendees</span>
            <input name="attendees" value={form.attendees} onChange={onChange} placeholder="Enter names or search..." />
          </label>

          <label>
            <span>Topics Discussed</span>
            <textarea name="topics_discussed" value={form.topics_discussed} onChange={onChange} placeholder="Enter key discussion points..." rows={5} />
          </label>

          <button type="button" className="secondary" onClick={() => dispatch(updateField({ name: "ai_summary", value: "Voice-note summary: efficacy discussed, HCP requested safety data, follow-up required." }))}>
            <Sparkles size={16} />
            Summarize from Voice Note
          </button>

          <div className="split-boxes">
            <label>
              <span>Materials Shared</span>
              <textarea name="materials_shared" value={form.materials_shared} onChange={onChange} placeholder="No materials added." rows={3} />
            </label>
            <label>
              <span>Samples Distributed</span>
              <textarea name="samples_distributed" value={form.samples_distributed} onChange={onChange} placeholder="No samples added." rows={3} />
            </label>
          </div>

          <fieldset>
            <legend>Observed/Inferred HCP Sentiment</legend>
            <div className="radio-row">
              {["Positive", "Neutral", "Negative"].map((sentiment) => (
                <label key={sentiment} className="radio">
                  <input type="radio" name="sentiment" value={sentiment} checked={form.sentiment === sentiment} onChange={onChange} />
                  {sentiment}
                </label>
              ))}
            </div>
          </fieldset>

          <label>
            <span>Outcomes</span>
            <textarea name="outcomes" value={form.outcomes} onChange={onChange} placeholder="Key outcomes or agreements..." rows={4} />
          </label>

          <label>
            <span>Follow-up Actions</span>
            <textarea name="follow_up_actions" value={form.follow_up_actions} onChange={onChange} placeholder="Enter next steps or tasks..." rows={4} />
          </label>

          <div className="suggestions">
            <span>AI Suggested Follow-ups:</span>
            {followUps.map((item) => (
              <button type="button" key={item} onClick={() => dispatch(applySuggestion(item))}>
                + {item}
              </button>
            ))}
          </div>

          <div className="form-actions">
            <button type="button" className="secondary" onClick={() => dispatch(resetForm())}>
              Clear
            </button>
            <button type="submit" disabled={status === "saving"}>
              <Save size={16} />
              {status === "saving" ? "Saving..." : "Save Log"}
            </button>
          </div>
        </form>

        <aside className="panel assistant">
          <div className="panel-header">
            <Activity size={18} />
            <div>
              <span>AI Assistant</span>
              <small>Log interaction via chat</small>
            </div>
          </div>

          <div className="messages">
            {chat.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
                <p>{message.text}</p>
                {message.data?.suggestions && (
                  <ul>
                    {message.data.suggestions.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                )}
                {message.data?.materials && (
                  <ul>
                    {message.data.materials.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>

          <form className="chat-form" onSubmit={onChat}>
            <input name="message" placeholder="Describe interaction..." />
            <button type="submit" disabled={status === "thinking"} aria-label="Send message">
              <Send size={17} />
            </button>
          </form>
        </aside>
      </section>

      <section className="history">
        <div className="section-title">
          <CalendarClock size={18} />
          <h2>Recent Interactions</h2>
        </div>
        <div className="history-grid">
          {items.length === 0 ? (
            <div className="empty-state">
              <Search size={20} />
              <span>No interactions logged yet.</span>
            </div>
          ) : (
            items.slice(0, 4).map((item) => (
              <article key={item.id} className="history-card">
                <div>
                  <strong>{item.hcp_name}</strong>
                  <span>{item.interaction_type}</span>
                </div>
                <p>{item.ai_summary || item.topics_discussed}</p>
                <footer>
                  <span>{item.sentiment}</span>
                  <span>{item.interaction_date}</span>
                </footer>
              </article>
            ))
          )}
        </div>
      </section>

      <section className="tool-strip" aria-label="LangGraph tools">
        {[
          ["Log Interaction", "Captures HCP notes, entities, summary"],
          ["Edit Interaction", "Updates logged CRM fields"],
          ["Suggest Follow-up", "Creates next best actions"],
          ["Recommend Materials", "Matches approved content"],
          ["Analyze Sentiment", "Classifies HCP sentiment"],
        ].map(([name, description]) => (
          <div key={name}>
            <FlaskConical size={16} />
            <strong>{name}</strong>
            <span>{description}</span>
          </div>
        ))}
      </section>
    </main>
  );
}
