import { useRouter } from 'next/router';
import { useState } from "react";

interface UploadedPage {
  id: number;
  content: string;
}

export default function Home() {
  const router = useRouter();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [generatedPages, setGeneratedPages] = useState<UploadedPage[]>([]);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    setIsGenerated(false); // Reset generated state when new file is uploaded
    setGeneratedPages([]); // Reset generated pages
  };

  const handleGenerate = async () => {
    if (!uploadedFile) return;
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('description', description);

      /* // Simulate API call with timeout
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Mock generated pages - replace this with your actual generation logic
      const pages: UploadedPage[] = [
        {
          id: 1,
          content: `# Generated Content\n\nThis is the generated content from your uploaded file: ${uploadedFile.name}\n\n\n\nDescription: ${description}\n\n`
        }
      ];
      setGeneratedPages(pages); */

      const response = await fetch('http://127.0.0.1:8000/api/generate', {  // Changed URL to point to FastAPI backend
        method: 'POST',
        body: formData,
        // No need to include credentials if you're not using cookies
      });

      if (!response.ok) {
        throw new Error('Failed to generate content');
      }

      const data = await response.json();
      setGeneratedPages(data.pages);
      setIsGenerated(true);
    } catch (error) {
      console.error('Error generating content:', error);
      alert('Failed to generate content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoToEditor = async () => {
    if (!isGenerated || generatedPages.length === 0) return;

    try {
      router.push({
        pathname: '/editor',
        query: {
          pages: JSON.stringify(generatedPages),
        }
      });
    } catch (error) {
      console.error('Error navigating to editor:', error);
      alert('Failed to navigate to editor. Please try again.');
    }
  };

  return (
    <div className="bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="min-h-screen pt-10">
        <div className="container mx-auto px-4 max-w-3xl text-center space-y-20">
          <img
            src="/assets/image.png"
            alt="Dilo"
            className="mx-auto w-64 object-contain"
          />

          <div className="bg-white p-8 rounded-2xl shadow-lg space-y-6">
            <h4 className="text-2xl font-bold text-gray-800">
              Upload your Sequence of images here 📄
            </h4>

            <div className="space-y-8">
              <div className="flex justify-center">
                <label className="flex flex-col items-center px-4 py-6 bg-white text-blue-600 rounded-lg shadow-lg border-2 border-blue-100 border-dashed hover:bg-blue-50 transition-colors cursor-pointer">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="mt-2 text-base">Choose a file</span>
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </label>
              </div>
              {/* Text Input */}
              <div className="max-w-xl mx-auto">
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add a description of what you want to generate..."
                  className="w-full px-4 py-3 text-gray-800 rounded-xl border-2 border-blue-100 
                           focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500
                           placeholder:text-gray-400
                           transition-all duration-200
                           min-h-[100px] resize-none
                           bg-white"
                />
              </div>
            </div>

            <div className="py-4">
              <p className={`text-lg font-medium ${isGenerated ? 'text-green-600' : 'text-gray-600'
                }`}>
                {!uploadedFile && "Please upload a file to continue"}
                {uploadedFile && !isGenerated && "File uploaded! Click Generate to process"}
                {uploadedFile && isGenerated && "Generation complete! 🚀"}
              </p>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={handleGenerate}
                disabled={!uploadedFile || isLoading || isGenerated}
                className={`
                  px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-200
                  flex items-center gap-2
                  ${!uploadedFile || isLoading || isGenerated
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-75 shadow-none'
                    : 'bg-gradient-to-r from-green-600 to-green-500 text-white shadow-lg hover:opacity-90 hover:shadow-green-200/50 shadow-green-200/30'
                  }
                `}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <span>⚡</span>
                    Generate
                  </>
                )}
              </button>

              <button
                onClick={handleGoToEditor}
                disabled={!isGenerated || isLoading}
                className={`
                  px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-200
                  flex items-center gap-2
                  ${!isGenerated || isLoading
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-75 shadow-none'
                    : 'bg-gradient-to-r from-violet-600 to-blue-500 text-white shadow-lg hover:opacity-90 hover:shadow-violet-200/50 shadow-violet-200/30'
                  }
                `}
              >
                <span>📝</span>
                Go to Editor
              </button>
            </div>
          </div>
        </div>
      </div>
    </div >
  );
}