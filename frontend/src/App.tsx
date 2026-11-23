import axios from "axios";
import Editor from "@monaco-editor/react";
import { useState } from "react";
import {
  Code2,
  LayoutDashboard,
  History,
  Settings,
  ArrowRightLeft,
  Sparkles,
  User,
  Plus,
} from "lucide-react";

function App() {
  const [sourceLanguage, setSourceLanguage] = useState("Python");
  const [targetLanguage, setTargetLanguage] = useState("JavaScript");
  const [code, setCode] = useState(
    'def greet(name):\n    print("Hello", name)\n\ngreet("World")'
  );
  const [apiMessage, setApiMessage] = useState("");
  const [translatedCode, setTranslatedCode] = useState("");
  const handleTranslate = async () => {
  try {
    setApiMessage("Connecting to CodeBridge backend...");

    const response = await axios.post(
      "http://127.0.0.1:8000/api/translate",
      {
        source_language: sourceLanguage,
        target_language: targetLanguage,
        code: code,
      }
    );

    setApiMessage(response.data.message);
    setTranslatedCode(response.data.translated_code);
  } catch (error) {
    console.error(error);
    setApiMessage("Could not connect to the backend. Check whether FastAPI is running.");
    setTranslatedCode("");
  }
};
  return (
    <div className="min-h-screen bg-slate-950 text-white flex">

      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 p-6 flex flex-col">
        <div className="flex items-center gap-3 mb-12">
          <Code2 className="text-cyan-400" size={30} />
          <h1 className="text-2xl font-bold">
            Code<span className="text-cyan-400">Bridge</span>
          </h1>
        </div>

        <nav className="space-y-3">
          <div className="flex items-center gap-3 bg-slate-800 text-cyan-400 p-3 rounded-lg">
            <LayoutDashboard size={20} />
            Dashboard
          </div>

          <div className="flex items-center gap-3 text-slate-400 p-3">
            <History size={20} />
            History
          </div>

          <div className="flex items-center gap-3 text-slate-400 p-3">
            <Settings size={20} />
            Settings
          </div>
        </nav>

        <div className="mt-auto text-slate-500 text-sm">
          CodeBridge v1.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">

        {/* Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3xl font-bold">Code Translator</h2>
            <p className="text-slate-400 mt-2">
              Translate code between programming languages.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-slate-800 p-3 rounded-full">
              <User size={20} />
            </div>
          </div>
        </header>

        {/* Welcome */}
        <section className="mb-8">
          <h3 className="text-xl font-semibold">
            Welcome to CodeBridge!
          </h3>
          <p className="text-slate-400 mt-1">
            Write your code, choose a language, and translate.
          </p>
        </section>

        {/* Language Selection */}
        <section className="flex items-center gap-4 mb-6">
          <select
            value={sourceLanguage}
            onChange={(e) => setSourceLanguage(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg p-3"
          >
            <option>Python</option>
            <option>JavaScript</option>
            <option>Java</option>
          </select>

          <ArrowRightLeft className="text-cyan-400" />

          <select
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg p-3"
          >
            <option>JavaScript</option>
            <option>Python</option>
            <option>Java</option>
          </select>
        </section>

        {/* Code Editor Area */}
        <section className="grid grid-cols-2 gap-5">

          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between">
              <span className="font-semibold">Source Code</span>
              <span className="text-cyan-400 text-sm">{sourceLanguage}</span>
            </div>

            <Editor
              height="320px"
              language={sourceLanguage.toLowerCase()}
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value ?? "")}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                automaticLayout: true,
                scrollBeyondLastLine: false,
                padding: { top: 15 },
               }}
             /> 
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between">
              <span className="font-semibold">Translated Code</span>
              <span className="text-cyan-400 text-sm">{targetLanguage}</span>
            </div>

            <Editor
              height="320px"
              language="javascript"
              theme="vs-dark"
              value={translatedCode}
              options={{
                readOnly: true,
                minimap: { enabled: false },
                fontSize: 14,
                automaticLayout: true,
                scrollBeyondLastLine: false,
                padding: { top: 15 },
              }}
            />
            <p className="text-sm text-cyan-400 mt-4">
               {apiMessage}
              </p>
          </div>

        </section>

        {/* Translate Button */}
        <div className="flex justify-end mt-6">
          <button 
           onClick={handleTranslate}
                     className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-6 py-3 rounded-lg"
          >
            <Sparkles size={18} />
            Translate Code
          </button>
        </div>

      </main>
    </div>
  );
}

export default App;
