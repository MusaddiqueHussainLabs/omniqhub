﻿using omniqhub.client.Interop;

namespace omniqhub.client.Pages.Applications
{
    public sealed partial class Chat
    {
        private const string AnswerElementId = "answers";

        private string _userQuestion = "";
        private UserQuestion _currentQuestion;
        private string _lastReferenceQuestion = "";
        private bool _isReceivingResponse = false;

        private readonly Dictionary<UserQuestion, ApproachResponse?> _questionAndAnswerMap = [];

        //[Inject] public required ISessionStorageService SessionStorage { get; set; }

        [Inject] public required ApiClient ApiClient { get; set; }

        [CascadingParameter(Name = nameof(Settings))]
        public required RequestSettingsOverrides Settings { get; set; }

        [CascadingParameter(Name = nameof(IsReversed))]
        public required bool IsReversed { get; set; }

        private Task OnAskQuestionAsync(string question)
        {
            _userQuestion = question;
            return OnAskClickedAsync();
        }

        private async Task OnAskClickedAsync()
        {
            if (string.IsNullOrWhiteSpace(_userQuestion))
            {
                return;
            }

            _isReceivingResponse = true;
            _lastReferenceQuestion = _userQuestion;
            _currentQuestion = new(_userQuestion, DateTime.Now);
            _questionAndAnswerMap[_currentQuestion] = null;

            try
            {
                var history = _questionAndAnswerMap
                    .Where(x => x.Value is not null)
                    .Select(x => new ChatTurn(x.Key.Question, x.Value!.answer))
                    .ToList();

                history.Add(new ChatTurn(_userQuestion));

                var request = new ChatRequest([.. history], Settings.Approach, Settings.Overrides);
                var result = await ApiClient.ChatConversationAsync(request);

                _questionAndAnswerMap[_currentQuestion] = result.Response;
                if (result.IsSuccessful)
                {
                    _userQuestion = "";
                    _currentQuestion = default;

                    //JavaScriptModule.ScrollIntoView(AnswerElementId);
                    //StateHasChanged();
                }
            }
            finally
            {
                _isReceivingResponse = false;
            }
        }

        private void OnClearChat()
        {
            _userQuestion = _lastReferenceQuestion = "";
            _currentQuestion = default;
            _questionAndAnswerMap.Clear();
        }
    }
}
