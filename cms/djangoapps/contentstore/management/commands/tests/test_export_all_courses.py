"""
Test for export all courses.
"""


import shutil
from tempfile import mkdtemp

import six

from contentstore.management.commands.export_all_courses import export_courses_to_output_path
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class ExportAllCourses(ModuleStoreTestCase):
    """
    Tests exporting all courses.
    """
    def setUp(self):
        """ Common setup. """
        super(ExportAllCourses, self).setUp()
        self.store = modulestore()._get_modulestore_by_type(ModuleStoreEnum.Type.mongo)
        self.temp_dir = mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        self.first_course = CourseFactory.create(
            org="test", course="course1", display_name="run1", default_store=ModuleStoreEnum.Type.mongo
        )
        self.second_course = CourseFactory.create(
            org="test", course="course2", display_name="run2", default_store=ModuleStoreEnum.Type.mongo
        )

    def test_export_all_courses(self):
        """
        Test exporting good and faulty courses
        """
        # check that both courses exported successfully
        courses, failed_export_courses = export_courses_to_output_path(self.temp_dir)
        self.assertEqual(len(courses), 2)
        self.assertEqual(len(failed_export_courses), 0)

        # manually make second course faulty and check that it fails on export
        second_course_id = self.second_course.id
        self.store.collection.update(
            {'_id.org': second_course_id.org, '_id.course': second_course_id.course, '_id.name': second_course_id.run},
            {'$set': {'metadata.tags': 'crash'}}
        )
        courses, failed_export_courses = export_courses_to_output_path(self.temp_dir)
        self.assertEqual(len(courses), 2)
        self.assertEqual(len(failed_export_courses), 1)
        self.assertEqual(failed_export_courses[0], six.text_type(second_course_id))
