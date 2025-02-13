# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""URL endpoint to record bad bisect."""

from google.appengine.api import users

from dashboard import oauth2_decorator
from dashboard import request_handler
from dashboard import utils
from dashboard import xsrf
from dashboard.models import try_job


class BadBisectHandler(request_handler.RequestHandler):

  @oauth2_decorator.DECORATOR.oauth_required
  def get(self):
    """Renders bad_bisect.html."""
    if not utils.IsValidSheriffUser():
      self._RenderError('No permission.')
      return
    if not self.request.get('try_job_id'):
      self._RenderError('Missing try_job_id.')
      return

    self.RenderHtml('bad_bisect.html',
                    {'try_job_id': self.request.get('try_job_id')})

  @xsrf.TokenRequired
  def post(self):
    """Handles post requests from bad_bisect.html."""
    if not utils.IsValidSheriffUser():
      self._RenderError('No permission.')
      return
    if not self.request.get('try_job_id'):
      self._RenderError('Missing try_job_id.')
      return

    try_job_id = int(self.request.get('try_job_id'))
    job = try_job.TryJob.get_by_id(try_job_id)
    if not job:
      self._RenderError('TryJob doesn\'t exist.')
      return

    user = users.get_current_user()
    if not job.bad_result_emails:
      job.bad_result_emails = set()
    if user.email() not in job.bad_result_emails:
      job.bad_result_emails.add(user.email())
      job.put()
      # TODO(chrisphan): Log results to quick_logger here.

    self.RenderHtml('result.html', {
        'headline': 'Confirmed bad bisect.  Thank you for reporting.'})

  def _RenderError(self, error):
    self.RenderHtml('result.html', {'errors': [error]})
