//
//  RegisterViewModel.h
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "NetManager.h"

@interface RegisterViewModel : NSObject
+ (void)registerWithNickName:(NSString *)nickName Email:(NSString *)email Psw:(NSString *)psw Psw2:(NSString *)pws2 Block:(StateBlock)block;
#pragma mark - Tools
+ (BOOL)isValidEmail:(NSString *)Email;
+ (BOOL)isVaildPsw:(NSString *)psw;
@end
