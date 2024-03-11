using MudBlazor;
using MudBlazor.ThemeManager;
using omniqhub.client.Theme;

namespace omniqhub.client.Components.Layout
{
    public sealed partial class MainLayout
    {
        private ThemeManagerTheme _themeManager = new ThemeManagerTheme();

        public bool _drawerOpen = true;
        public bool _themeManagerOpen = false;

        void DrawerToggle()
        {
            _drawerOpen = !_drawerOpen;
        }

        void OpenThemeManager(bool value)
        {
            _themeManagerOpen = value;
        }

        void UpdateTheme(ThemeManagerTheme value)
        {
            _themeManager = value;
            StateHasChanged();
        }

        protected override void OnInitialized()
        {
            _themeManager.Theme = new MudBlazorAdminDashboard();
            _themeManager.DrawerClipMode = DrawerClipMode.Always;
            _themeManager.FontFamily = "Montserrat";
            _themeManager.DefaultBorderRadius = 3;
        }

        private List<BreadcrumbItem> _items = new List<BreadcrumbItem>
        {
            new BreadcrumbItem("Personal", href: "#"),
            new BreadcrumbItem("Dashboard", href: "#"),
        };
    }
}
