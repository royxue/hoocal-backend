//
//  RegisterViewModel.m
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "RegisterViewModel.h"
#import "SignInViewModel.h"

@implementation RegisterViewModel
+ (void)registerWithNickName:(NSString *)nickName Email:(NSString *)email Psw:(NSString *)psw Psw2:(NSString *)pws2 Block:(StateBlock)block {
    if (!(nickName && nickName.length > 0)) {
        if (block) {
            block(failed, nil);
            return;
        }
    }
    if (![RegisterViewModel isVaildPsw:email]) {
        if (block) {
            block(failed, nil);
        }
        return;
    }
    if (![RegisterViewModel isVaildPsw:psw]) {
        if (block) {
            block(failed, nil);
        }
        return;
    }
    if (![RegisterViewModel isCorrectPswWhenRegisterWithPws:psw Psw2:pws2]) {
        if (block) {
            block(failed, nil);
        }
        return;
    }
    [[NetManager shareInstance] requestForRegisterWithNickName:nickName Email:email Psw:psw Block:^(NSInteger state, NSDictionary *dict) {
        if (state == successful) {
            [SignInViewModel signWithEmail:email Psw:psw Block:^(NSInteger state, NSDictionary *dict) {
                if (state == successful) {
                    block(successful, nil);
                } else {
                    block(failed, nil);
                }
            }];
        } else {
            block(failed, nil);
        }
    }];
    
}
#pragma mark - Tools
+ (BOOL)isValidEmail:(NSString *)Email {
    if ((Email && Email.length > 0 && ([Email rangeOfString:@"@"].location != NSNotFound))) {
        return YES;
    }
    return NO;
}

+ (BOOL)isVaildPsw:(NSString *)psw {
    if (psw && psw.length >= 6) {
        return YES;
    }
    return NO;
}

+ (BOOL)isCorrectPswWhenRegisterWithPws:(NSString *)psw Psw2:(NSString *)psw2 {
    if (!psw) {
        return NO;
    }
    if (!psw2) {
        return NO;
    }
    if ([psw isEqualToString:psw2]) {
        return YES;
    } else {
        return NO;
    }
}
@end
