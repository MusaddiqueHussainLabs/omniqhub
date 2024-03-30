using static MudBlazor.CategoryTypes;
using System.Net;

namespace omniqhub.client.Pages.Authentication
{
    public partial class Login
    {
        #region Private Properties
        [Inject] private NavigationManager NavigationManager { get; set; }
        [Inject] public required ApiClient Client { get; set; }
        [Inject] public required ISnackbar Snackbar { get; set; }
        private bool PasswordVisibility { get; set; }
        private InputType PasswordInput { get; set; } = InputType.Password;
        private string PasswordInputIcon { get; set; } = Icons.Material.Filled.VisibilityOff;
        private LoginCommand LoginCommand { get; } = new();

        #endregion Private Properties

        protected override void OnInitialized()
        {
            LoginCommand.Email = "johndoe";
            LoginCommand.Password = "password";
        }

        private async Task LoginUser()
        {
            var response = await Client.Login(LoginCommand);
            if (response != null)
            {
                NavigationManager.NavigateTo("/personal/dashboard");
            }
            else
            {
                Snackbar.Add(
                        "Unauthorized access...",
                        Severity.Error,
                        static options =>
                        {
                            options.ShowCloseIcon = true;
                            options.VisibleStateDuration = 10_000;
                        });
            }

            //var responseWrapper = await AccountsClient.Login(LoginCommand);

            //if (responseWrapper.IsSuccessStatusCode)
            //{
            //    if (responseWrapper.Payload.RequiresTwoFactor)
            //    {
            //        NavigationManager.NavigateTo($"account/loginWith2Fa/{LoginCommand.Email}");
            //        AppStateManager.UserPasswordFor2Fa = LoginCommand.Password;
            //    }
            //    else
            //    {
            //        await AuthenticationService.Login(responseWrapper.Payload.AuthResponse);
            //        var returnUrl = await ReturnUrlProvider.GetReturnUrl();
            //        await ReturnUrlProvider.RemoveReturnUrl();
            //        NavigationManager.NavigateTo(returnUrl);
            //    }
            //}
            //else
            //{
            //    EditContextApiExceptionFallback.PopulateFormErrors(responseWrapper.ApiErrorResponse);
            //    SnackbarApiExceptionProvider.ShowErrors(responseWrapper.ApiErrorResponse);
            //}
        }

        private void TogglePasswordVisibility()
        {
            if (PasswordVisibility)
            {
                PasswordVisibility = false;
                PasswordInputIcon = Icons.Material.Filled.VisibilityOff;
                PasswordInput = InputType.Password;
            }
            else
            {
                PasswordVisibility = true;
                PasswordInputIcon = Icons.Material.Filled.Visibility;
                PasswordInput = InputType.Text;
            }
        }
    }
}
