// Root app

const App = () => {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);
  const [activeCase, setActiveCase] = React.useState(null);
  const [route, setRoute] = React.useState(() => (window.location.hash || "#top").slice(1) || "top");

  const normalizedRoute = route === "home" ? "top" : route;
  const isHomeRoute = normalizedRoute === "top";

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  React.useEffect(() => {
    const onHashChange = () => {
      setRoute((window.location.hash || "#top").slice(1) || "top");
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    };
    onHashChange();
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  React.useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") { setMenuOpen(false); setActiveCase(null); } };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  React.useEffect(() => {
    document.body.style.overflow = (menuOpen || activeCase) ? "hidden" : "";
  }, [menuOpen, activeCase]);

  const renderRoute = () => {
    switch (normalizedRoute) {
      case "services":
        return (
          <React.Fragment>
            <Services />
            <IntakeBasics />
            <ClientSegments />
            <Standards />
          </React.Fragment>
        );
      case "trust":
        return (
          <React.Fragment>
            <ProofNumbers />
            <Trust />
          </React.Fragment>
        );
      case "cases":
        return (
          <React.Fragment>
            <Cases onOpen={setActiveCase} />
            <ClientVoices />
          </React.Fragment>
        );
      case "process":
        return <Process />;
      case "faq":
        return <Faq />;
      case "media":
        return <Media />;
      case "about":
        return <About />;
      case "team":
        return <Team />;
      case "contacts":
        return <Contacts />;
      default:
        return <Hero />;
    }
  };

  return (
    <React.Fragment>
      <Nav onOpenMenu={() => setMenuOpen(true)} scrolled={scrolled} />
      <Drawer open={menuOpen} onClose={() => setMenuOpen(false)} />
      <main id="main-content" className={isHomeRoute ? "main-home" : "main-section"}>
        {renderRoute()}
      </main>
      {!isHomeRoute && <Footer />}
      <CaseModal data={activeCase} onClose={() => setActiveCase(null)} />
    </React.Fragment>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
