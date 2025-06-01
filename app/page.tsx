import Header from "@/components/Header";
import QueryInput from "@/components/QueryInput";
import StatCard from "@/components/StatCard";
import ChartContainer from "@/components/ChartContainer";
import InsightSection from "@/components/InsightSection";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header />
      <main className="flex-grow container mx-auto p-4 md:p-8">
        <QueryInput />

        <section className="my-8">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Stats Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Example Stat Cards - these would be populated with real data */}
            <StatCard title="Avg Points Per Game" value="25.6" />
            <StatCard title="Total Rebounds" value="1,204" />
            <StatCard title="Assist/Turnover Ratio" value="2.1" />
          </div>
        </section>

        <section className="my-8">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Chart Section</h2>
          <ChartContainer />
        </section>

        <section className="my-8">
          <InsightSection />
        </section>

      </main>
      <footer className="bg-gray-800 text-white p-4 text-center">
        <p>&copy; {new Date().getFullYear()} HoopSense. All rights reserved.</p>
      </footer>
    </div>
  );
}
