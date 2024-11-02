// pages/editor.tsx
import type { NextPage } from 'next';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

// Add these imports at the top of your editor.tsx
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

interface MarkdownPage {
    id: number;
    description: string;
    image?: string;
    content: string;

}

const convertMarkdown = (markdown: string): string => {
    return markdown
        .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" width="500" class="max-w-full h-auto my-2" />')
        .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold my-4 text-black">$1</h1>')
        .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold my-3 text-black">$1</h2>')
        .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold my-2 text-black">$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-4 rounded-lg my-2"><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
        .replace(/^\- (.*$)/gm, '<li class="ml-4 text-black">$1</li>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-blue-500 hover:underline">$1</a>')
        .replace(/^(?!<[h|l|p|u])(.*$)/gm, '<p class="my-2 text-black">$1</p>');
};

const Editor: NextPage = () => {
    const mockPages = [
        {
            id: 1, content: `# Welcome to Page 1

            This page has a local image:
            
            ![Logo](/assets/dilo_5.jpg)
            
            ## More content
            You can add text around your images...`,
            description: 'This is the first page',
        },
        { id: 2, content: "# Product Overview\n\n## Description\nOur product helps you create beautiful documentation.\n\n## Benefits\n- Fast\n- Reliable\n- Secure", description: 'This is the second page' },
        { id: 3, content: "# Getting Started\n\n## Installation\n```bash\nnpm install my-package\n```\n\n## Usage\nFollow these steps...", description: 'This is the third page' },
        { id: 4, content: "# Advanced Features\n\n## Custom Themes\nYou can customize the appearance...\n\n## Plugins\nExtend functionality with plugins...", description: 'This is the fourth page' },
        { id: 5, content: "# Support\n\n## Contact\nReach out to us at...\n\n## FAQ\nCommonly asked questions...", description: 'This is the fifth page' },
    ];

    const router = useRouter();
    const [pages, setPages] = useState<MarkdownPage[]>([]);
    const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [improveText, setImproveText] = useState<string>('');
    const [isImproving, setIsImproving] = useState<boolean>(false);

    // Add this function in your Editor component
    const generatePDF = async () => {
        const pdf = new jsPDF('p', 'pt', 'a4');

        // For each page in pages array
        for (let i = 0; i < pages.length; i++) {
            // Create a temporary div to render the markdown
            const temp = document.createElement('div');
            temp.className = 'prose max-w-none p-8';
            temp.style.width = '800px';
            temp.innerHTML = convertMarkdown(pages[i].content);
            document.body.appendChild(temp);

            try {
                // Convert the rendered markdown to canvas
                const canvas = await html2canvas(temp, {
                    scale: 3,
                    useCORS: true,
                    logging: false
                });

                // Add page to PDF
                const imgData = canvas.toDataURL('image/png');
                if (i > 0) {
                    pdf.addPage();
                }

                // Calculate dimensions to fit page
                const imgProps = pdf.getImageProperties(imgData);
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

                pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);

                // Clean up
                document.body.removeChild(temp);
            } catch (err) {
                console.error('Error generating PDF page:', err);
            }
        }

        // Save the PDF
        pdf.save('markdown-document.pdf');
    };
    const improvePage = async () => {
        if (!improveText.trim()) {
            alert('Please enter what you want to improve');
            return;
        }

        setIsImproving(true);

        try {
            // Mock API call
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Mock improved content - in reality this would come from your API
            const improvedContent = `# Improved Version\n\n${pages[currentPageIndex].content}\n\n## Improvements Made\nBased on your request: "${improveText}"\n\n- Enhanced the content structure\n- Improved clarity and readability\n- Added relevant examples`;

            console.log("ecco")
            console.log(pages[currentPageIndex].description)
            console.log(improveText)
            console.log(pages[currentPageIndex].image)
            //call api
            const response = await fetch('http://127.0.0.1:8000/improveText', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    description: pages[currentPageIndex].description,
                    improveText,
                    image: pages[currentPageIndex].image
                })
            });

            if (!response.ok) {
                throw new Error(`API call failed: ${response.statusText}`);
            }

            const data = await response.json();

            if (!data.improved_content) {
                throw new Error('No improved content received from API');
            }

            // Create the new content using the page_instruction from the response
            const newContent = `# Step ${pages[currentPageIndex].id}\n\n${data.improved_content}\n\n![Step ${pages[currentPageIndex].id}](${pages[currentPageIndex].image})`;

            // Update the current page with improved content
            const updatedPages = [...pages];
            updatedPages[currentPageIndex] = {
                ...updatedPages[currentPageIndex],
                content: newContent
            };

            setPages(updatedPages);
            setImproveText(''); // Clear the improve input
        } catch (error) {
            console.error('Error improving page:', error);
            alert('Failed to improve the page. Please try again.');
        } finally {
            setIsImproving(false);
        }
    };


    // Fetch pages data
    // Get the initial content from router query
    useEffect(() => {
        const fetchPages = async () => {
            try {
                setIsLoading(true);

                // Check if we have content from the file upload
                if (router.query.pages) {
                    const pagesData = JSON.parse(router.query.pages as string) as MarkdownPage[];
                    // set content to "`# Step ${pages[i].id}\n\n${pages[i].content}\n\n![Step ${pages[i].id}](${pages[i].image})`"
                    pagesData.forEach((page) => {
                        page.content = `# Step ${page.id}\n\n${page.description}\n\n![Step ${page.id}](${page.image})`;
                    });
                    setPages(pagesData);
                } else {
                    // Fall back to mock pages if no uploaded content
                    setPages(mockPages);
                }



                setError(null);
            } catch (err) {
                setError('Failed to load pages. Please try again later.');
                console.error('Error fetching pages:', err);
            } finally {
                setIsLoading(false);
            }
        };

        if (router.isReady) {
            fetchPages();
        }
    }, [router.isReady, router.query.initialContent]);

    const handlePrevPage = () => {
        if (currentPageIndex > 0) {
            setCurrentPageIndex(currentPageIndex - 1);
        }
    };

    const handleNextPage = () => {
        if (currentPageIndex < pages.length - 1) {
            setCurrentPageIndex(currentPageIndex + 1);
        }
    };

    const handleContentChange = (newContent: string) => {
        const updatedPages = [...pages];
        const currentPage = updatedPages[currentPageIndex];

        // Replace the placeholder with the actual image path
        let finalContent = newContent.replace(
            /!\[Step \d+\]\s?\(image\)/g,
            `![Step ${currentPage.id}](${currentPage.image})`
        );

        // If there's no image placeholder but we have an image, append it
        if (currentPage.image && !finalContent.includes(currentPage.image)) {
            finalContent = `${finalContent}\n\n![Step ${currentPage.id}](${currentPage.image})`;
        }

        updatedPages[currentPageIndex] = {
            ...currentPage,
            content: finalContent
        };
        setPages(updatedPages);
    };
    // Function to clean up the display of markdown content
    const getDisplayContent = (content: string): string => {
        const currentPage = pages[currentPageIndex];
        if (!currentPage) return content;

        // Replace the full image path/base64 with a placeholder
        return content.replace(
            /!\[Step \d+\]\([^\)]+\)/g,
            `![Step ${currentPage.id}] (image)`
        );
    };

    const handleSave = async () => {
        try {
            // In a real app, this would be an API call to save the changes
            // await fetch('/api/pages', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(pages)
            // });

            // Simulating API delay
            await new Promise(resolve => setTimeout(resolve, 500));
            console.log('Pages saved successfully:', pages);

            // You could show a success message here
            alert('Changes saved successfully!');
        } catch (err) {
            console.error('Error saving pages:', err);
            alert('Failed to save changes. Please try again.');
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-black">Loading pages...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <div className="text-center text-red-600">
                    <p>{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <main className="container mx-auto p-6 space-y-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <button
                        onClick={() => router.push('/')}
                        className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-sm hover:bg-gray-50 transition-colors">
                        ← Back
                    </button>
                    <h1 className="text-2xl font-bold">Markdown Editor</h1>
                    <button
                        onClick={generatePDF}
                        className="px-4 py-2 bg-gradient-to-r from-green-600 to-green-500 text-white rounded-xl shadow-sm hover:opacity-90 transition-opacity"
                    >
                        Export PDF
                    </button>
                </div>



                {/* Navigation */}
                {/* Navigation and Controls */}
                <div className="flex justify-between items-center gap-4 bg-white p-4 rounded-xl shadow-sm">
                    <h2 className="text-lg font-medium">
                        Page {currentPageIndex + 1} of {pages.length}
                    </h2>
                    <div className="flex items-center gap-4">
                        <div className="flex gap-2">
                            <textarea
                                rows={1}
                                value={improveText}
                                onChange={(e) => setImproveText(e.target.value)}
                                disabled={isImproving}
                                className="w-64 p-3 text-sm bg-gray-50 rounded-xl border focus:ring-2 focus:ring-violet-500/50 resize-none"
                                placeholder="Write what you want to improve..."
                            />
                            <button
                                onClick={improvePage}
                                disabled={isImproving || !improveText.trim()}
                                className="px-6 py-2 bg-gradient-to-r from-violet-600 to-blue-500 text-white rounded-xl shadow-sm hover:opacity-90 disabled:opacity-50 transition-opacity flex items-center gap-2"
                            >
                                {isImproving ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                        </svg>
                                        Improving...
                                    </>
                                ) : (
                                    <>✨ Improve</>
                                )}
                            </button>
                        </div>

                        <div className="flex gap-2">
                            <button
                                onClick={handlePrevPage}
                                disabled={currentPageIndex === 0}
                                className={`p-2 rounded-xl transition-all ${currentPageIndex === 0
                                    ? 'bg-gray-100 opacity-50 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-violet-600 to-blue-500 text-white shadow-sm hover:opacity-90'
                                    }`}
                            >
                                <span className={`text-2xl ${currentPageIndex === 0 ? 'grayscale' : ''}`}>⬅️</span>
                            </button>
                            <button
                                onClick={handleNextPage}
                                disabled={currentPageIndex === pages.length - 1}
                                className={`p-2 rounded-xl transition-all ${currentPageIndex === pages.length - 1
                                    ? 'bg-gray-100 opacity-50 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-violet-600 to-blue-500 text-white shadow-sm hover:opacity-90'
                                    }`}
                            >
                                <span className={`text-2xl ${currentPageIndex === pages.length - 1 ? 'grayscale' : ''}`}>➡️</span>
                            </button>
                            <button
                                onClick={handleSave}
                                className="px-6 py-2 bg-gradient-to-r from-violet-600 to-blue-500 text-white rounded-xl shadow-sm hover:opacity-90 transition-opacity flex items-center gap-2"
                            >
                                <span>💾</span>
                                Save
                            </button>
                        </div>
                    </div>
                </div>

                {/* Editor */}
                <div className="grid grid-cols-2 gap-6 bg-white p-6 rounded-xl shadow-sm">
                    <div className="space-y-2">
                        <h3 className="font-medium">Markdown</h3>
                        <textarea
                            value={getDisplayContent(pages[currentPageIndex]?.content || '')}
                            onChange={(e) => handleContentChange(e.target.value)}
                            className="w-full h-[600px] p-4 font-mono text-sm bg-gray-50 rounded-xl border focus:ring-2 focus:ring-violet-500/50 resize-none"
                            placeholder="Enter your markdown here..."
                        />
                    </div>
                    <div className="space-y-2">
                        <h3 className="font-medium">Preview</h3>
                        <div
                            className="w-full h-[600px] p-4 bg-gray-50 rounded-xl border overflow-auto prose max-w-none"
                            dangerouslySetInnerHTML={{
                                __html: convertMarkdown(pages[currentPageIndex]?.content || '')
                            }}
                        />
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Editor;