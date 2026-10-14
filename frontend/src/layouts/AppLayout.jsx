import { Layout, Typography } from "antd";
const { Header, Content, Footer } = Layout;
export function AppLayout({ accentColor, children }) {
  return (
    <Layout
      className="app-shell"
    >
      <Header
        className="app-header"
      >
        <div
          className="app-header__inner"
        >
          <span
            className="app-logo"
            style={{ background: accentColor }}
            aria-hidden="true"
          />
          <div>
            <Typography.Title
              level={4}
              style={{ margin: 0, lineHeight: 1.2 }}
            >Climate Hazard Trends</Typography.Title>
            <Typography.Text
              type="secondary"
              className="app-subtitle"
            >Historical heatwaves, heavy rainfall and drought for any region</Typography.Text>
          </div>
        </div>
      </Header>
      <Content
        className="app-content"
      >
        {children}
      </Content>
      <Footer
        className="app-footer"
      >Data: Open-Meteo (ERA5 reanalysis) · Map: OpenStreetMap contributors</Footer>
    </Layout>
  );
}
