# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import mock
import unittest

from apiclient import errors

from dashboard import issue_tracker_service
from dashboard import testing_common


@mock.patch('issue_tracker_service.discovery.build', mock.MagicMock())
class IssueTrackerServiceTest(testing_common.TestCase):

  def testAddBugComment_Basic(self):
    service = issue_tracker_service.IssueTrackerService()
    service._MakeCommentRequest = mock.Mock()
    self.assertTrue(service.AddBugComment(12345, 'The comment'))
    self.assertEqual(1, service._MakeCommentRequest.call_count)
    service._MakeCommentRequest.assert_called_with(
        12345, {'updates': {}, 'content': 'The comment'})

  def testAddBugComment_WithNoBug_ReturnsFalse(self):
    service = issue_tracker_service.IssueTrackerService()
    service._MakeCommentRequest = mock.Mock()
    self.assertFalse(service.AddBugComment(None, 'Some comment'))
    self.assertFalse(service.AddBugComment(-1, 'Some comment'))

  def testAddBugComment_WithOptionalParameters(self):
    service = issue_tracker_service.IssueTrackerService()
    service._MakeCommentRequest = mock.Mock()
    self.assertTrue(service.AddBugComment(
        12345, 'Some other comment', status='Fixed',
        labels=['Foo'], cc_list=['someone@chromium.org']))
    self.assertEqual(1, service._MakeCommentRequest.call_count)
    service._MakeCommentRequest.assert_called_with(
        12345,
        {
            'updates': {
                'status': 'Fixed',
                'cc': ['someone@chromium.org'],
                'labels': ['Foo'],
            },
            'content': 'Some other comment'
        })

  def testAddBugComment_MergeBug(self):
    service = issue_tracker_service.IssueTrackerService()
    service._MakeCommentRequest = mock.Mock()
    self.assertTrue(service.AddBugComment(12345, 'Dupe', merge_issue=54321))
    self.assertEqual(1, service._MakeCommentRequest.call_count)
    service._MakeCommentRequest.assert_called_with(
        12345,
        {
            'updates': {
                'status': 'Duplicate',
                'mergedInto': 54321,
            },
            'content': 'Dupe'
        })

  @mock.patch('logging.error')
  def testAddBugComment_Error(self, mock_logging_error):
    service = issue_tracker_service.IssueTrackerService()
    service._ExecuteRequest = mock.Mock(return_value=None)
    self.assertFalse(service.AddBugComment(12345, 'My bug comment'))
    self.assertEqual(1, service._ExecuteRequest.call_count)
    self.assertEqual(1, mock_logging_error.call_count)

  def testNewBug_Success_NewBugReturnsId(self):
    service = issue_tracker_service.IssueTrackerService()
    service._ExecuteRequest = mock.Mock(return_value={'id': 333})
    bug_id = service.NewBug('Bug title', 'body', owner='someone@chromium.org')
    self.assertEqual(1, service._ExecuteRequest.call_count)
    self.assertEqual(333, bug_id)

  def testNewBug_Failure_NewBugReturnsNone(self):
    service = issue_tracker_service.IssueTrackerService()
    service._ExecuteRequest = mock.Mock(return_value={})
    bug_id = service.NewBug('Bug title', 'body', owner='someone@chromium.org')
    self.assertEqual(1, service._ExecuteRequest.call_count)
    self.assertIsNone(bug_id)

  def testNewBug_UsesExpectedParams(self):
    service = issue_tracker_service.IssueTrackerService()
    service._MakeCreateRequest = mock.Mock()
    service.NewBug('Bug title', 'body', owner='someone@chromium.org')
    service._MakeCreateRequest.assert_called_with(
        {
            'title': 'Bug title',
            'summary': 'Bug title',
            'description': 'body',
            'labels': [],
            'components': [],
            'status': 'Assigned',
            'owner': {'name': 'someone@chromium.org'},
        })

  def testMakeCommentRequest_UserDoesNotExist_RetryMakeCommentRequest(self):
    service = issue_tracker_service.IssueTrackerService()
    error_content = {
        'error': {'message': 'The user does not exist', 'code': 404}
    }
    service._ExecuteRequest = mock.Mock(side_effect=errors.HttpError(
        mock.Mock(return_value={'status': 404}), json.dumps(error_content)))
    service.AddBugComment(12345, 'The comment', owner='test@chromium.org')
    self.assertEqual(2, service._ExecuteRequest.call_count)

  def testMakeCommentRequest_IssueDeleted_ReturnsTrue(self):
    service = issue_tracker_service.IssueTrackerService()
    error_content = {
        'error': {'message': 'User is not allowed to view this issue 12345',
                  'code': 403}
    }
    service._ExecuteRequest = mock.Mock(side_effect=errors.HttpError(
        mock.Mock(return_value={'status': 403}), json.dumps(error_content)))
    comment_posted = service.AddBugComment(12345, 'The comment',
                                           owner='test@chromium.org')
    self.assertEqual(1, service._ExecuteRequest.call_count)
    self.assertEqual(True, comment_posted)


if __name__ == '__main__':
  unittest.main()
