/*
 * File:   sound_processor_bell.hpp
 * Author: themylogin
 *
 * Created on Aug 12, 2013, 5:52:25 PM
 */

#ifndef SOUND_PROCESSOR_BELL_HPP
#define	SOUND_PROCESSOR_BELL_HPP

#include <cppunit/extensions/HelperMacros.h>

class sound_processor_bell : public CPPUNIT_NS::TestFixture {
    CPPUNIT_TEST_SUITE(sound_processor_bell);

    CPPUNIT_TEST(testBell);

    CPPUNIT_TEST_SUITE_END();

public:
    sound_processor_bell();
    virtual ~sound_processor_bell();
    void setUp();
    void tearDown();

private:
    void testBell();
};

#endif	/* SOUND_PROCESSOR_BELL_HPP */

