
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
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

function App() {
  const [sourceLanguage, setSourceLanguage] = useState("Python");
  const [targetLanguage, setTargetLanguage] = useState("JavaScript");

  const [code, setCode] = useState(
    'def greet(name):\n    print("Hello", name)\n\ngreet("World")'
  );

  const [apiMessage, setApiMessage] = useState("");
  const [translatedCode, setTranslatedCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(false);

  const handleTranslate = async () => {
    if (!code.trim()) {
      setApiMessage("Please enter some code to translate.");
      setErrorMessage(true);
      setTranslatedCode("");
      return;
    }

    if (sourceLanguage === targetLanguage) {
      setApiMessage("Please select two different languages.");
      setErrorMessage(true);
      setTranslatedCode("");
      return;
    }

    try {
      setLoading(true);
      setErrorMessage(false);
      setApiMessage("Translating your code...");
      setTranslatedCode("");

      const response = await axios.post(
        "http://127.0.0.1:8000/api/translate",
        {
          source_language: sourceLanguage,
          target_language: targetLanguage,
          code: code,
        }
      );

      setTranslatedCode(response.data.translated_code);
      setApiMessage(response.data.message);
      setErrorMessage(false);

    } catch (error) {
      console.error(error);

      const message = axios.isAxiosError(error)
        ? error.response?.data?.detail ||
          "Could not connect to the backend. Check whether FastAPI is running."
        : "An unexpected error occurred.";

      setApiMessage(message);
      setTranslatedCode("");
      setErrorMessage(true);

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#5680E9] text-white">

      {/* SIDEBAR */}

      <aside className="hidden md:flex w-64 shrink-0 bg-[#101A31] border-r border-[#C1C8E4]/20 p-6 flex-col">

        {/* Logo */}

        <div className="flex items-center gap-3 mb-14">
          <div className="bg-[#5680E9]/20 p-2 rounded-xl">
            <Code2 className="text-[#5AB9EA]" size={30} />
          </div>

          <h1 className="text-2xl font-bold tracking-tight">
            Code<span className="text-[#5680E9]">Bridge</span>
          </h1>
        </div>

        {/* Navigation */}

        <nav className="space-y-3">

          <div className="flex items-center gap-3 bg-[#5680E9]/20 text-[#84CEEB] border border-[#5680E9]/30 p-3 rounded-xl cursor-pointer">
            <LayoutDashboard size={20} />
            <span className="font-medium">Dashboard</span>
          </div>

          <div className="flex items-center gap-3 text-[#C1C8E4] hover:bg-[#84CEEB]/10 hover:text-white p-3 rounded-xl cursor-pointer transition">
            <History size={20} />
            History
          </div>

          <div className="flex items-center gap-3 text-[#C1C8E4] hover:bg-[#84CEEB]/10 hover:text-white p-3 rounded-xl cursor-pointer transition">
            <Settings size={20} />
            Settings
          </div>

        </nav>

        {/* Sidebar Bottom */}

        <div className="mt-auto">

          <div className="bg-[#5680E9]/10 border border-[#5680E9]/20 rounded-xl p-4 mb-5">
            <div className="flex items-center gap-2 text-[#84CEEB] mb-2">
              <Sparkles size={17} />
              <span className="text-sm font-semibold">
                CodeBridge
              </span>
            </div>

            <p className="text-xs text-[#C1C8E4] leading-relaxed">
              Your intelligent programming language translator.
            </p>
          </div>

          <p className="text-[#C1C8E4]/60 text-xs">
            CodeBridge v1.0
          </p>

        </div>

      </aside>


      {/* MAIN CONTENT */}

      <main className="flex-1 min-w-0 p-5 md:p-8 lg:p-10">

        {/* HEADER */}

        <header className="flex justify-between items-center mb-10">

          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-[#5AB9EA]"></span>
              <span className="text-xs text-[#84CEEB] uppercase tracking-widest">
                CodeBridge Workspace
              </span>
            </div>

            <h2 className="text-2xl md:text-3xl font-bold">
              Code Translator
            </h2>

            <p className="text-[#C1C8E4] mt-2 text-sm md:text-base">
              Translate code between programming languages.
            </p>
          </div>

          <button className="bg-[#5680E9]/20 border border-[#5680E9]/30 p-3 rounded-full hover:bg-[#5680E9]/40 transition">
            <User size={21} className="text-[#84CEEB]" />
          </button>

        </header>


        {/* WELCOME SECTION */}

        <section className="mb-8">

          <h3 className="text-xl font-semibold">
            Welcome to CodeBridge!
          </h3>

          <p className="text-[#C1C8E4] mt-2 text-sm">
            Write your code, select your languages, and let CodeBridge do the rest.
          </p>

        </section>


        {/* LANGUAGE SELECTION */}

        <section className="bg-[#101A31] border border-[#C1C8E4]/20 rounded-2xl p-5 mb-7">

          <div className="flex items-center gap-2 mb-4">
            <ArrowRightLeft size={18} className="text-[#5AB9EA]" />

            <h3 className="font-semibold text-sm">
              Select Languages
            </h3>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-4">

            {/* Source Language */}

            <div className="w-full flex-1">

              <label className="text-xs text-[#C1C8E4] mb-2 block">
                SOURCE LANGUAGE
              </label>

              <select
                value={sourceLanguage}
                onChange={(e) => setSourceLanguage(e.target.value)}
                className="w-full bg-[#172443] border border-[#5680E9]/40 rounded-xl p-3 text-white outline-none focus:border-[#5AB9EA] transition"
              >
                <option>Python</option>
                <option>JavaScript</option>
                <option>Java</option>
              </select>

            </div>

            {/* Direction Icon */}

            <div className="bg-[#5680E9]/20 border border-[#5680E9]/30 p-3 rounded-xl mt-5 sm:mt-0">
              <ArrowRightLeft className="text-[#84CEEB]" size={21} />
            </div>

            {/* Target Language */}

            <div className="w-full flex-1">

              <label className="text-xs text-[#C1C8E4] mb-2 block">
                TARGET LANGUAGE
              </label>

              <select
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                className="w-full bg-[#172443] border border-[#5680E9]/40 rounded-xl p-3 text-white outline-none focus:border-[#5AB9EA] transition"
              >
                <option>JavaScript</option>
                <option>Python</option>
                <option>Java</option>
              </select>

            </div>

          </div>

        </section>


        {/* CODE EDITORS */}

        <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">

          {/* SOURCE EDITOR */}

          <div className="bg-[#101A31] border border-[#5680E9]/30 rounded-2xl overflow-hidden shadow-lg">

            <div className="p-4 flex justify-between items-center border-b border-[#C1C8E4]/20">

              <div>
                <h3 className="font-semibold">
                  Source Code
                </h3>

                <p className="text-xs text-[#C1C8E4] mt-1">
                  Write or paste your code
                </p>
              </div>

              <span className="bg-[#5680E9]/20 text-[#84CEEB] border border-[#5680E9]/30 text-xs px-3 py-1.5 rounded-lg">
                {sourceLanguage}
              </span>

            </div>

            <Editor
              height="360px"
              language={sourceLanguage.toLowerCase()}
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value ?? "")}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                automaticLayout: true,
                scrollBeyondLastLine: false,
                padding: { top: 18 },
                roundedSelection: true,
                cursorSmoothCaretAnimation: "on",
              }}
            />

            <div className="px-4 py-3 border-t border-[#C1C8E4]/20 flex justify-between text-xs text-[#C1C8E4]">
              <span>Input Editor</span>
              <span>{code.length} characters</span>
            </div>

          </div>


          {/* OUTPUT EDITOR */}

          <div className="bg-[#101A31] border border-[#8860D0]/40 rounded-2xl overflow-hidden shadow-lg">

            <div className="p-4 flex justify-between items-center border-b border-[#C1C8E4]/20">

              <div>
                <h3 className="font-semibold">
                  Translated Code
                </h3>

                <p className="text-xs text-[#C1C8E4] mt-1">
                  Your translated result appears here
                </p>
              </div>

              <span className="bg-[#8860D0]/20 text-[#C1C8E4] border border-[#8860D0]/40 text-xs px-3 py-1.5 rounded-lg">
                {targetLanguage}
              </span>

            </div>

            <Editor
              height="360px"
              language={targetLanguage.toLowerCase()}
              theme="vs-dark"
              value={translatedCode}
              options={{
                readOnly: true,
                minimap: { enabled: false },
                fontSize: 14,
                automaticLayout: true,
                scrollBeyondLastLine: false,
                padding: { top: 18 },
                roundedSelection: true,
              }}
            />

            <div className="px-4 py-3 border-t border-[#C1C8E4]/20 flex justify-between text-xs text-[#C1C8E4]">
              <span>Output Editor</span>
              <span>{translatedCode.length} characters</span>
            </div>

          </div>

        </section>


        {/* TRANSLATION STATUS */}

        {apiMessage && (

          <div className={`mt-5 flex items-center gap-3 rounded-xl p-4 border ${
            errorMessage
              ? "bg-red-500/10 border-red-400/30 text-red-300"
              : "bg-[#5680E9]/10 border-[#5680E9]/30 text-[#84CEEB]"
          }`}>

            {loading ? (
              <Loader2 size={19} className="animate-spin" />
            ) : errorMessage ? (
              <AlertCircle size={19} />
            ) : (
              <CheckCircle2 size={19} />
            )}

            <p className="text-sm">
              {apiMessage}
            </p>

          </div>

        )}


        {/* TRANSLATE BUTTON */}

        <div className="flex justify-end mt-7">

          <button
            onClick={handleTranslate}
            disabled={loading}
            className="flex items-center justify-center gap-3 bg-[#0B1020] hover:bg-[#101A31] disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold px-7 py-3.5 rounded-xl shadow-lg shadow-black/20 transition-all duration-200 hover:-translate-y-0.5"
          >

            {loading ? (
              <Loader2 size={19} className="animate-spin" />
            ) : (
              <Sparkles size={19} />
            )}

            {loading ? "Translating..." : "Translate Code"}

          </button>

        </div>


        {/* FOOTER */}

        <footer className="mt-12 pt-6 border-t border-[#C1C8E4]/20 text-center">

          <p className="text-xs text-[#C1C8E4]/60">
            CodeBridge — Making programming language translation simpler.
          </p>

        </footer>

      </main>

    </div>
  );
}

export default App;
