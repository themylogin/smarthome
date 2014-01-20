/*
 * File:   sound_processor_code.hpp
 * Author: themylogin
 *
 * Created on Aug 4, 2013, 6:09:21 PM
 */

#ifndef SOUND_PROCESSOR_CODE_HPP
#define	SOUND_PROCESSOR_CODE_HPP

#include <cppunit/extensions/HelperMacros.h>

class sound_processor_code : public CPPUNIT_NS::TestFixture
{
    CPPUNIT_TEST_SUITE(sound_processor_code);

    CPPUNIT_TEST(testKnock1);
    CPPUNIT_TEST(testKnock2);
    CPPUNIT_TEST(testNoKnock1);

    CPPUNIT_TEST_SUITE_END();

public:
    sound_processor_code();
    virtual ~sound_processor_code();
    void setUp();
    void tearDown();

private:
    void testKnock1();
    void testKnock2();
    void testNoKnock1();
    
    void testFromFile(std::string file, bool hasCode);
};

#endif	/* SOUND_PROCESSOR_CODE_HPP */

